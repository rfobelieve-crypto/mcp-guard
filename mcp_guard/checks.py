# -*- coding: utf-8 -*-
"""五項檢查。全部基於靜態事實，不執行目標程式碼。

嚴重度：CRITICAL > HIGH > MEDIUM > LOW > INFO
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from .fetch import RepoBundle
from .profile import CAP_ZH, ENV, EVAL_, EXEC, FS, NET
from .profile import infer as infer_profile

CRITICAL, HIGH, MEDIUM, LOW, INFO = "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"


@dataclass
class Finding:
    check: str          # 檢查項（繁中）
    severity: str
    title: str
    detail: str
    evidence: str = ""


def _age_days(iso: str) -> float | None:
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - t).total_seconds() / 86400
    except Exception:
        return None


# ── 1. 身分與存在性 ─────────────────────────────────────────────────────────
# 這一項就是 watch-mcp 那種案例：被大力宣傳、實際 404、名字任人搶註。

def check_identity(b: RepoBundle) -> list[Finding]:
    out: list[Finding] = []
    if not b.slug:
        out.append(Finding("身分", CRITICAL, "找不到對應的原始碼倉庫",
                           "這個目標無法對應到任何 GitHub repo，等於沒有可稽核的原始碼。"
                           "任何安裝指令都不該照著執行。"))
        return out

    if not b.exists:
        if not b.owner_exists:
            out.append(Finding(
                "身分", CRITICAL, f"倉庫與作者帳號都不存在（{b.slug}）",
                "GitHub 上查無此 repo，連作者帳號本身都沒註冊過。"
                "這代表安裝指令指向一個空名字——**任何人都可以搶先註冊這個名稱**，"
                "之後照著指令安裝的人裝到的會是陌生人放的程式碼（名稱搶註／供應鏈投毒）。",
                evidence=f"GET /repos/{b.slug} → 404；GET /users/{b.slug.split('/')[0]} → 404"))
        else:
            out.append(Finding(
                "身分", CRITICAL, f"倉庫不存在或非公開（{b.slug}）",
                "作者帳號存在，但這個 repo 查不到。可能已刪除、改名或轉為私有；"
                "同樣有「名稱被他人接手」的風險。",
                evidence=f"GET /repos/{b.slug} → 404"))
        return out

    m = b.meta
    created, pushed = m.get("created_at", ""), m.get("pushed_at", "")
    stars = m.get("stargazers_count", 0)
    age = _age_days(created)

    if age is not None and age < 30:
        out.append(Finding(
            "身分", HIGH, f"倉庫非常新（建立於 {age:.0f} 天前）",
            "新建立的 repo 本身不等於惡意，但若它同時被大量宣傳、或使用了"
            "熱門既有名稱，要特別留意是否為搶註／仿冒。", evidence=created[:10]))

    if m.get("archived"):
        out.append(Finding("身分", MEDIUM, "倉庫已封存（archived）",
                           "作者已停止維護，不會再修安全問題。"))

    if not m.get("license"):
        out.append(Finding("身分", LOW, "沒有授權條款（License）",
                           "沒有 LICENSE 檔，法律上你其實沒有被授權使用或散布。"))

    out.append(Finding(
        "身分", INFO, "倉庫基本資料",
        f"⭐ {stars}｜fork {m.get('forks_count', 0)}｜"
        f"語言 {m.get('language') or '未標示'}｜"
        f"建立 {created[:10]}｜最後推送 {pushed[:10]}"))
    return out


# ── 2. 供應鏈 ───────────────────────────────────────────────────────────────

INSTALL_HOOKS = ("preinstall", "postinstall", "install", "prepare", "prepublish")


def check_supply_chain(b: RepoBundle) -> list[Finding]:
    out: list[Finding] = []
    pkg_raw = b.files.get("package.json")
    if pkg_raw:
        try:
            pkg = json.loads(pkg_raw)
        except json.JSONDecodeError:
            pkg = {}
        scripts = pkg.get("scripts") or {}
        for hook in INSTALL_HOOKS:
            if hook in scripts:
                sev = HIGH if hook in ("preinstall", "postinstall", "install") else MEDIUM
                out.append(Finding(
                    "供應鏈", sev, f"安裝時會自動執行腳本：{hook}",
                    "npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。"
                    "這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。",
                    evidence=f'"{hook}": "{str(scripts[hook])[:160]}"'))
        deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})}
        floating = [f"{k}@{v}" for k, v in deps.items()
                    if isinstance(v, str) and (v.startswith("^") or v.startswith("~") or v == "*")]
        if len(floating) > 0:
            out.append(Finding(
                "供應鏈", LOW, f"有 {len(floating)} 個依賴未鎖定版本",
                "依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。",
                evidence="、".join(floating[:6]) + ("…" if len(floating) > 6 else "")))

    # npm 套件與 repo 是否互相對應（typosquatting 的基本防線）
    if b.npm_name:
        if not b.npm:
            out.append(Finding(
                "供應鏈", INFO, f"npm 上查無此套件（{b.npm_name}）",
                "原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。"))
        else:
            # 2026-07-27 校準：初版只要 slug 不出現在 repository 欄位就判
            # 「來源不一致」，結果 BrowserMCP/mcp 與 idosal/git-mcp 都誤報——
            # 它們的 repository 欄位根本是**空的**。缺少中繼資料 ≠ 造假，
            # 兩者的處置也完全不同，必須分開判。
            raw = b.npm.get("repository", "")
            repo_url = raw.get("url", "") if isinstance(raw, dict) else str(raw)
            if not repo_url.strip():
                out.append(Finding(
                    "供應鏈", LOW, "npm 套件未標示原始碼位置",
                    "套件沒有填 repository 欄位，因此**無法自動核對**它是否真的"
                    "由這個 repo 建置。這不代表有問題，但也代表少了一道可驗證性；"
                    "安裝前建議自行確認發布者身分。",
                    evidence=f"npm: {b.npm_name}（repository 欄位空白）"))
            elif b.slug and b.slug.lower() not in repo_url.lower():
                out.append(Finding(
                    "供應鏈", HIGH, "npm 套件標示的倉庫與實際來源不一致",
                    "套件明確指向的 repo 跟我們稽核的這個不是同一個。"
                    "這可能是改名／monorepo，也可能是仿冒（typosquatting），需人工確認。",
                    evidence=f"npm repository={repo_url[:120]}｜稽核對象={b.slug}"))
    return out


# ── 3. 權限面 ───────────────────────────────────────────────────────────────

# 能力偵測樣式 → (能力代號, 說明)
# 嚴重度不寫死在這裡：同一個能力，是否可疑取決於它宣稱的用途（見 profile.py）。
PERM_PATTERNS = [
    (r"child_process|subprocess\.|os\.system|execSync|spawnSync|Runtime\.getRuntime",
     EXEC, "會執行外部指令 / 開子行程",
     "這個 MCP 能在你的電腦上執行系統指令。"),
    (r"\beval\s*\(|new Function\s*\(|exec\s*\(\s*compile", EVAL_,
     "使用 eval / 動態執行程式碼",
     "動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。"),
    (r"fs\.(readFile|writeFile|unlink|rm)|shutil\.|pathlib\.|open\s*\(",
     FS, "會讀寫本機檔案",
     "確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。"),
    (r"process\.env|os\.environ|getenv", ENV, "會讀取環境變數",
     "環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。"),
]

SECRET_HINT = re.compile(
    r"[A-Z_]*(API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY)[A-Z_]*", re.I)
# 需為合法網域（含點、TLD 至少兩個英文字母），避免把 https://... 這類
# 文件裡的省略寫法誤判成主機
URL_RE = re.compile(r"https?://((?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,})")
SAFE_HOSTS = {
    "github.com", "raw.githubusercontent.com", "api.github.com", "registry.npmjs.org",
    "pypi.org", "modelcontextprotocol.io", "localhost", "127.0.0.1", "example.com",
    "schemas.modelcontextprotocol.io", "www.w3.org", "json-schema.org",
}


def check_permissions(b: RepoBundle) -> list[Finding]:
    """依「宣稱用途」判斷每個能力是本份還是越權。

    2026-07-27 加入用途比對：先前所有「會開子行程」一律判 HIGH，導致 18 個
    專案有 15 個是同一個 🟡，完全沒有區辨度——但桌面控制類 MCP 開 shell 本來
    就是它的功能。真正該示警的是「超出它自己宣稱範圍」的能力。
    """
    out: list[Finding] = []
    _code, profile_zh, expected = infer_profile(b)
    hits: dict[str, list[str]] = {}
    hosts: dict[str, str] = {}
    secrets: set[str] = set()

    for path, text in b.files.items():
        if path.lower().endswith((".md", ".txt")):
            continue
        for pat, cap, title, detail in PERM_PATTERNS:
            if re.search(pat, text):
                hits.setdefault(f"{cap}|{title}|{detail}", []).append(path)
        for host in URL_RE.findall(text):
            if host.lower() not in SAFE_HOSTS and not host.endswith(".local"):
                hosts.setdefault(host, path)
        secrets.update(s.upper() if isinstance(s, str) else s[0].upper()
                       for s in SECRET_HINT.findall(text))

    out.append(Finding(
        "權限", INFO, f"判定用途：{profile_zh}",
        "以下權限均以此用途為基準判斷是否合理。"
        f"這類工具預期會用到：{'、'.join(CAP_ZH[c] for c in sorted(expected))}。"))

    for key, paths in hits.items():
        cap, title, detail = key.split("|", 2)
        ev = "、".join(sorted(paths)[:5])
        if cap in expected:
            # 本份能力：仍要讓使用者知道，但不該和越權混為一談
            out.append(Finding(
                "權限", LOW, f"{title}（符合宣稱用途）",
                f"{detail}「{profile_zh}」類工具本來就需要這個能力，"
                "屬預期範圍；重點是你**知情**並給予對應的信任。", evidence=ev))
        else:
            out.append(Finding(
                "權限", HIGH, f"⚠ {title}（超出宣稱用途）",
                f"{detail}但它自述是「{profile_zh}」，這類用途通常**不需要**"
                "這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。",
                evidence=ev))

    # eval 幾乎沒有正當理由，即使落在預期能力內也單獨提醒
    if any(k.startswith(EVAL_) for k in hits):
        out.append(Finding(
            "權限", MEDIUM, "使用動態執行（eval）需額外留意",
            "eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自"
            "外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。"))

    if hosts:
        listed = "、".join(f"{h}" for h in sorted(hosts)[:10])
        out.append(Finding(
            "權限", MEDIUM if len(hosts) > 3 else LOW,
            f"會連往 {len(hosts)} 個外部主機",
            "確認這些連線是功能必需的，而不是把你的資料送到第三方。",
            evidence=listed + ("…" if len(hosts) > 10 else "")))

    if secrets:
        out.append(Finding(
            "權限", INFO, "需要的憑證類設定",
            "安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。",
            evidence="、".join(sorted(secrets)[:8])))
    return out


# ── 4. 工具描述投毒（MCP 特有攻擊面）────────────────────────────────────────
# MCP 的 tool description 會被直接餵給模型，等於一段「模型看得到、你看不到」的
# 提示詞。攻擊者可在其中夾帶指令（tool poisoning），或用不可見字元藏匿內容。

# 嚴重度依「有沒有正當用途」分級，不是依關鍵字命中與否。
#
# 2026-07-27 校準：初版把所有命中一律判 CRITICAL，結果對 Figma-Context-MCP、
# git-mcp、Windows-MCP、DesktopCommanderMCP 四個知名專案全部誤報——因為正常
# 的 MCP 本來就會寫「always call this tool first」（幫模型選對工具的路由提示）
# 、本來就會提到 .env（它就是檔案／環境變數工具）。關鍵字命中 ≠ 投毒意圖。
# 誤報對真實專案是不實指控，比漏報更該避免，因此改成下列分級：
#   CRITICAL 只留「找不到正當理由」的手法（要求忽略指令、要求隱瞞、隱藏字元）
#   其餘一律降級為需人工判讀的提示。
INJECTION_PATTERNS = [
    # ── 無正當用途：正常說明文字不會這樣寫 ──
    (r"ignore\s+(all\s+)?(the\s+)?previous|disregard\s+(the\s+)?(above|previous)|"
     r"忽略(前面|上述|之前|先前)", CRITICAL, "要求模型忽略先前指令",
     "正常的工具說明沒有任何理由叫模型忽略既有指令。這是提示詞注入的典型開頭。"),
    (r"do\s*not\s+(tell|inform|reveal|mention)\s+(the\s+)?user|"
     r"don'?t\s+tell\s+the\s+user|without\s+(telling|informing)\s+the\s+user|"
     r"不要(告訴|通知|讓)(使用者|用戶|用户)", CRITICAL, "要求模型對使用者隱瞞",
     "要求模型隱瞞自身行為，沒有正當用途——這正是資料外送類攻擊會做的事。"),

    # ── 有正當用途，但也是投毒常見載體：降級為人工判讀 ──
    (r"always\s+call|you\s+must\s+first|before\s+using\s+any\s+other\s+tool|"
     r"務必先|必須先(呼叫|調用|使用)", LOW, "描述含「優先呼叫本工具」的措辭",
     "這在正常 MCP 中很常見（引導模型選對工具），但也是投毒用來搶奪呼叫權的手法。"
     "請確認它引導的方向合理、且沒有附帶額外指令。"),
    (r"<\s*system\s*>|\[\s*system\s*\]|system\s+prompt|系統提示詞", MEDIUM,
     "描述中出現系統提示詞標記或字樣",
     "描述裡出現 <system> 之類的標記，可能是想偽裝成系統訊息。請確認上下文。"),
    (r"\.ssh/|id_rsa|BEGIN\s+(RSA|OPENSSH)\s+PRIVATE\s+KEY|私鑰", MEDIUM,
     "描述中提及金鑰或 SSH 路徑",
     "若這個工具本來就處理金鑰檔案屬正常；否則要問為什麼描述需要提到它。"),
]

# 測試／範例／fixture 檔含大量樣本字串，拿它們當證據會產生大量誤報
TEST_PATH_RE = re.compile(
    r"(^|/)(tests?|__tests__|__mocks__|spec|fixtures?|examples?|e2e|samples?)(/|$)"
    r"|\.(test|spec)\.[jt]sx?$|(^|/)test_[^/]+\.py$|_test\.py$", re.I)

# 零寬、雙向覆寫、BOM、私有區——正常說明文字不會用到
HIDDEN_CHARS = re.compile(r"[​-‏‪-‮⁠-⁤﻿-]")

# MCP 工具描述會出現在三種寫法，三種都要抓，否則投毒檢查會漏掉整個生態：
#   1. 明寫 description 欄位（JS/TS 物件、Python kwarg）
#   2. Python 以 @mcp.tool() 裝飾的函式 → 描述放在 docstring
#   3. JS 的 server.tool("名稱", "描述", …) 位置參數寫法
DESC_FIELD_RE = re.compile(
    r"""(?:description|instructions)\s*[:=]\s*(?P<q>["'`])(?P<body>.*?)(?<!\\)(?P=q)""",
    re.S | re.I)

# @mcp.tool(...) / @server.tool / @tool 之後第一個函式的 docstring
DESC_DOCSTRING_RE = re.compile(
    r"""@\w[\w.]*tool\w*\s*(?:\([^)]*\))?\s*(?:async\s+)?def\s+\w+\s*\(.*?\)"""
    r"""[^:\n]*:\s*(?P<q>\"\"\"|''')(?P<body>.*?)(?P=q)""",
    re.S | re.I)

# server.tool("name", "description", …) 位置參數
DESC_POSITIONAL_RE = re.compile(
    r"""\.(?:tool|registerTool|addTool)\s*\(\s*["'`][^"'`]{1,80}["'`]\s*,\s*"""
    r"""(?P<q>["'`])(?P<body>.*?)(?<!\\)(?P=q)""",
    re.S)

DESC_PATTERNS = (DESC_FIELD_RE, DESC_DOCSTRING_RE, DESC_POSITIONAL_RE)


def iter_descriptions(text: str):
    """吐出這個檔案裡所有工具描述字串（三種寫法合併、去重）。"""
    seen = set()
    for pat in DESC_PATTERNS:
        for m in pat.finditer(text):
            body = m.group("body")
            if body and body not in seen:
                seen.add(body)
                yield body


def check_tool_poisoning(b: RepoBundle) -> list[Finding]:
    out: list[Finding] = []
    scanned = 0
    seen: set[tuple[str, str]] = set()     # (嚴重度, 標題) 去重，同型只報一次
    for path, text in b.files.items():
        if path.lower().endswith((".md", ".txt", ".yml", ".yaml")):
            continue
        if TEST_PATH_RE.search(path):      # 測試／範例檔的樣本字串不算證據
            continue
        for body in iter_descriptions(text):
            scanned += 1
            matched = [(sev, label, why) for pat, sev, label, why
                       in INJECTION_PATTERNS if re.search(pat, body, re.I)]
            if not matched:
                continue

            # 組合判定：單一關鍵字容易誤報（正常工具也會這樣寫），但同一段
            # 描述同時命中多種不同手法，就很難用正當用途解釋 → 升級為嚴重。
            if len(matched) >= 2:
                labels = "、".join(l for _s, l, _w in matched)
                if ("combo", labels) not in seen:
                    seen.add(("combo", labels))
                    out.append(Finding(
                        "工具描述投毒", CRITICAL,
                        "同一段工具描述命中多種注入手法",
                        "MCP 的 tool description 會直接進入模型上下文，使用者通常"
                        f"看不到。這段描述同時出現：{labels}。單獨一項可能是巧合，"
                        "多項並存很難用正常功能解釋。",
                        evidence=f"{path}｜「{body.strip()[:140]}」"))
                continue

            sev, label, why = matched[0]
            if (sev, label) in seen:
                continue
            seen.add((sev, label))
            lead = ("MCP 的 tool description 會直接進入模型上下文，使用者通常"
                    "看不到。" if sev == CRITICAL else "")
            out.append(Finding(
                "工具描述投毒", sev, label, lead + why,
                evidence=f"{path}｜「{body.strip()[:120]}」"))
            if len(body) > 1500 and ("long", "") not in seen:
                seen.add(("long", ""))
                out.append(Finding(
                    "工具描述投毒", LOW, "工具描述異常冗長",
                    "長描述在功能複雜的工具上很常見，但也是把指令埋在人不會滑到"
                    "的位置的手法。若前面沒有其他命中，通常不必緊張。",
                    evidence=f"{path}｜長度 {len(body)} 字"))

        for hit in HIDDEN_CHARS.finditer(text):
            out.append(Finding(
                "工具描述投毒", CRITICAL, "原始碼含不可見／雙向覆寫字元",
                "零寬字元或 bidi 覆寫字元可讓「你讀到的程式碼」與「實際執行的程式碼」"
                "不一致，也可用來在工具描述中藏匿指令。正常原始碼沒有理由出現它們。",
                evidence=f"{path}｜位置 {hit.start()}｜U+{ord(hit.group()):04X}"))
            break   # 每個檔案報一次就夠

    if not out:
        out.append(Finding(
            "工具描述投毒", INFO,
            f"未發現可疑工具描述（已掃描 {scanned} 段 description）",
            "沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，"
            "但常見的 tool poisoning 手法都沒有命中。"))
    return out


# ── 5. 維護活躍度 ───────────────────────────────────────────────────────────

def check_maintenance(b: RepoBundle) -> list[Finding]:
    if not b.exists:
        return []
    out: list[Finding] = []
    pushed = b.meta.get("pushed_at", "")
    days = _age_days(pushed)
    if days is None:
        return out
    if days > 365:
        out.append(Finding("維護", HIGH, f"超過 {days/30:.0f} 個月沒有更新",
                           "長期停更的專案不會跟進 MCP 規格變動，也不會修安全問題。",
                           evidence=f"最後推送 {pushed[:10]}"))
    elif days > 180:
        out.append(Finding("維護", MEDIUM, f"約 {days/30:.0f} 個月沒有更新",
                           "更新頻率偏低，導入前先確認它仍相容你的 MCP 客戶端。",
                           evidence=f"最後推送 {pushed[:10]}"))
    else:
        out.append(Finding("維護", INFO, f"最近 {days:.0f} 天內有更新",
                           "專案仍在活躍維護中。", evidence=f"最後推送 {pushed[:10]}"))
    if (n := b.meta.get("open_issues_count", 0)) > 50:
        out.append(Finding("維護", LOW, f"未處理 issue 偏多（{n} 則）",
                           "可能代表維護者回應不及，遇到問題時求助無門。"))
    return out


ALL_CHECKS = (check_identity, check_supply_chain, check_permissions,
              check_tool_poisoning, check_maintenance)


def run_all(b: RepoBundle) -> list[Finding]:
    findings: list[Finding] = []
    for fn in ALL_CHECKS:
        try:
            findings.extend(fn(b))
        except Exception as e:      # 單項壞掉不該讓整份報告掛掉
            findings.append(Finding(fn.__name__, INFO, "此項檢查執行失敗",
                                    f"{type(e).__name__}: {e}"))
    return findings
