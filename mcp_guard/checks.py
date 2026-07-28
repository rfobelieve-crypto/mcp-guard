# -*- coding: utf-8 -*-
"""五項檢查。全部基於靜態事實，不執行目標程式碼。

嚴重度：CRITICAL > HIGH > MEDIUM > LOW > INFO
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from . import agentfiles
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

    out.extend(_check_registry(b))

    out.append(Finding(
        "身分", INFO, "倉庫基本資料",
        f"⭐ {stars}｜fork {m.get('forks_count', 0)}｜"
        f"語言 {m.get('language') or '未標示'}｜"
        f"建立 {created[:10]}｜最後推送 {pushed[:10]}"))
    return out


# 官方 registry 的登錄狀態。**這一段只陳述發布者身分被驗證到什麼程度，
# 完全不是程式碼安全性的背書**——登錄只需要證明「我是這個帳號／網域的人」，
# 不需要通過任何內容審查。措辭必須守住這條線。
REG_DETAIL = {
    "official": ("這個 MCP 由 MCP 官方團隊自己發布。這代表發布者身分明確，"
                 "**不代表**它的權限比較小或程式碼比較安全——下面的權限"
                 "與投毒檢查仍然照跑。"),
    "domain": ("發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個"
               "真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分"
               "不是程式碼**。"),
    "github": ("發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並"
               "登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。"),
}


def _check_registry(b: RepoBundle) -> list[Finding]:
    reg = b.registry
    if not reg:
        return []
    if not reg.get("registered"):
        return [Finding(
            "身分", LOW, "未登錄官方 MCP registry",
            "這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。"
            "很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何"
            "第三方驗證過「發布者是誰」，你得自己確認來源。")]
    kind = reg.get("kind", "github")
    return [Finding(
        "身分", INFO, f"官方 registry：{reg.get('label', '已登錄')}",
        REG_DETAIL.get(kind, REG_DETAIL["github"]),
        evidence=f"registry 名稱 {reg.get('name', '')}")]


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

    out.extend(_check_python_supply(b))
    return out


# ── 2b. Python 生態的供應鏈 ─────────────────────────────────────────────────
# 2026-07-28：18 個掃描目標中有 10 個供應鏈檢查完全落空，Python 專案 4 個
# 全中——因為原本只讀 package.json。而 Python 的安裝期執行點其實更隱蔽：
# `pip install` 會直接把 setup.py 當程式跑，沒有 postinstall 那種明確欄位。

# setup.py 幾乎人人都有，光是存在不構成風險；有風險的是它在安裝當下做什麼。
# 依「有沒有正當理由」分級，和第 4 項的校準原則一致。
#
# 2026-07-28 校準（對 googleapis/mcp-toolbox 的真實誤報）：初版三條規則
# 都太寬。命中的關鍵字要能對應到「安裝當下真的會發生的事」，否則就是在
# 指控正常的打包寫法：
#   · 裸 urllib      → `import urllib.parse` 只是解析網址，根本沒連網
#   · 裸 cmdclass    → 覆寫 bdist_wheel 是**建置期**（打包者端）的正當做法，
#                      內含二進位檔的套件都得這樣寫，使用者安裝時不會跑
#   · 裸 exec(       → `exec(open("_version.py").read())` 是讀版本號的常見寫法
SETUP_PATTERNS = [
    (r"urlopen|urlretrieve|requests\s*\.\s*(get|post|put)|"
     r"httpx\s*\.\s*(get|post|Client)|socket\s*\.\s*(socket|create_connection)|"
     r"\bcurl\s+http|\bwget\s+http",
     HIGH, "setup.py 會在安裝時連線網路",
     "`pip install` 會直接執行 setup.py。在那個時間點連外，代表實際安裝到的"
     "內容由對方伺服器當下決定——你稽核過的原始碼管不到它。"),
    (r"base64\s*\.\s*b64decode|codecs\s*\.\s*decode|marshal\s*\.\s*loads|"
     r"zlib\s*\.\s*decompress",
     HIGH, "setup.py 含編碼或壓縮過的內容",
     "安裝腳本沒有正當理由需要解碼混淆內容，這是隱藏真實行為最常見的手法。"),
    # 只抓**安裝期**指令。bdist_wheel／sdist／build_ext 屬於建置期，
    # 由打包者執行而不是使用者，不列入。
    (r"cmdclass\s*=\s*\{[^}]{0,400}?[\"'](install|develop|install_lib|"
     r"install_scripts)[\"']\s*:|"
     r"class\s+\w+\s*\(\s*_?(install|develop)\s*\)",
     HIGH, "setup.py 覆寫了安裝期指令",
     "它以自訂類別接管 install／develop 步驟，等同 npm 的 postinstall："
     "你還沒開始用，程式碼已經跑過一次了。"),
    (r"\bsubprocess\b|os\s*\.\s*system|os\s*\.\s*popen",
     MEDIUM, "setup.py 會在安裝時執行外部指令",
     "常見的正當用途是呼叫 git 取版本號或編譯原生模組；"
     "但這確實是安裝當下就會執行的程式碼，值得逐行讀懂。"),
    (r"\bexec\s*\(|\beval\s*\(",
     LOW, "setup.py 使用動態執行",
     "讀版本號時寫 `exec(open('_version.py').read())` 是常見的正當做法。"
     "確認被執行的內容來自這個 repo 內的檔案，而不是下載或解碼來的。"),
]

# 標準建置後端。清單外的後端不等於惡意，但它會在安裝時被下載並執行。
KNOWN_BACKENDS = ("setuptools", "hatchling", "flit", "poetry", "pdm",
                  "maturin", "scikit_build", "scikit-build", "meson",
                  "mesonpy", "setuptools_scm", "hatch")

PY_DEP_RE = re.compile(r"^\s*[\"']([A-Za-z0-9._-]+)\s*([^\"']*)[\"']\s*,?\s*$", re.M)

# 註解與 docstring 不會在安裝時被執行，比對前先剝掉——否則說明文字裡
# 出現的 subprocess 之類的字眼會被當成證據。
COMMENT_RE = re.compile(r"#[^\n]*")
DOCSTRING_RE = re.compile(r'"""[\s\S]*?"""' + r"|'''[\s\S]*?'''")


def _check_python_supply(b: RepoBundle) -> list[Finding]:
    out: list[Finding] = []
    pyproject = b.files.get("pyproject.toml")

    # monorepo（例如 awslabs/mcp）在 src/*/ 下各有一份打包檔，而**每一個
    # setup.py 都會在安裝對應套件時執行**——只看根目錄等於漏掉全部子套件。
    setups = {p: t for p, t in b.files.items()
              if p == "setup.py" or p.endswith("/setup.py")}
    hits: dict[tuple, list[str]] = {}
    for path, text in sorted(setups.items()):
        # 註解與 docstring 不會被執行，先剝掉再比對，避免拿說明文字當證據
        code = DOCSTRING_RE.sub("", COMMENT_RE.sub("", text))
        for pat, sev, title, detail in SETUP_PATTERNS:
            m = re.search(pat, code, re.I)
            if m:
                line = code[:m.start()].count("\n") + 1
                hits.setdefault((sev, title, detail, m.group()[:60]),
                                []).append(f"{path}:{line}")
    for (sev, title, detail, snippet), where in hits.items():
        ev = f"{where[0]}｜{snippet}"
        if len(where) > 1:
            ev += f"（另 {len(where) - 1} 個 setup.py 相同）"
        out.append(Finding("供應鏈", sev, title, detail, evidence=ev))

    if pyproject:
        m = re.search(r"build-backend\s*=\s*[\"']([^\"']+)", pyproject)
        if m:
            backend = m.group(1)
            root = backend.split(".")[0].split(":")[0].lower()
            if root not in KNOWN_BACKENDS:
                out.append(Finding(
                    "供應鏈", MEDIUM, "使用非標準的建置後端",
                    "建置後端會在安裝時被下載並執行。這可能是合理的專案選擇，"
                    "但那個後端本身也需要被信任——請確認它是什麼。",
                    evidence=f"build-backend={backend}"))

        dep = re.search(r"^\s*dependencies\s*=\s*\[(.*?)\]", pyproject,
                        re.M | re.S)
        if dep:
            floating = [f"{n}{v}".strip() for n, v in PY_DEP_RE.findall(dep.group(1))
                        if not v.strip() or v.strip().startswith((">", "^", "~", "!"))]
            if floating:
                out.append(Finding(
                    "供應鏈", LOW, f"有 {len(floating)} 個依賴未鎖定版本",
                    "依賴沒有釘死版本，代表未來安裝時拉到的新版可能與你稽核過的"
                    "內容不同。",
                    evidence="、".join(floating[:6]) + ("…" if len(floating) > 6 else "")))

    # PyPI 與原始碼是否互相對應（與 npm 那段同一道防線）
    if b.pypi_name:
        if not b.pypi:
            out.append(Finding(
                "供應鏈", INFO, f"PyPI 上查無此套件（{b.pypi_name}）",
                "原始碼宣告了套件名但 PyPI 查不到，代表尚未發佈或用其他方式散布。"))
        else:
            info = b.pypi.get("info") or {}
            urls = {k.lower(): v for k, v in (info.get("project_urls") or {}).items()}
            home = " ".join(str(v) for v in urls.values()) + " " + str(info.get("home_page") or "")
            if not home.strip():
                out.append(Finding(
                    "供應鏈", LOW, "PyPI 套件未標示原始碼位置",
                    "套件沒有填任何專案連結，因此**無法自動核對**它是否真的由這個 "
                    "repo 建置。這不代表有問題，但也代表少了一道可驗證性。",
                    evidence=f"PyPI: {b.pypi_name}"))
            elif b.slug and b.slug.lower() not in home.lower():
                out.append(Finding(
                    "供應鏈", HIGH, "PyPI 套件標示的倉庫與實際來源不一致",
                    "套件指向的 repo 跟我們稽核的這個不是同一個。這可能是改名／"
                    "monorepo，也可能是仿冒（typosquatting），需人工確認。",
                    evidence=f"PyPI 連結={home.strip()[:110]}｜稽核對象={b.slug}"))
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

# 這兩個手法「不管載體是什麼都沒有正當用途」，工具描述與代理指令檔（第 6 項）
# 共用同一份定義——拆成兩份會隨時間漂移，改了一邊忘了另一邊等於開一個洞。
RE_IGNORE_PRIOR = (
    r"ignore\s+(all\s+)?(the\s+)?previous|disregard\s+(the\s+)?(above|previous)|"
    r"忽略(前面|上述|之前|先前)")
RE_HIDE_FROM_USER = (
    r"do\s*not\s+(tell|inform|reveal|mention)\s+(the\s+)?user|"
    r"don'?t\s+tell\s+the\s+user|without\s+(telling|informing)\s+the\s+user|"
    r"不要(告訴|通知|讓)(使用者|用戶|用户)")

INJECTION_PATTERNS = [
    # ── 無正當用途：正常說明文字不會這樣寫 ──
    (RE_IGNORE_PRIOR, CRITICAL, "要求模型忽略先前指令",
     "正常的工具說明沒有任何理由叫模型忽略既有指令。這是提示詞注入的典型開頭。"),
    (RE_HIDE_FROM_USER, CRITICAL, "要求模型對使用者隱瞞",
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

# 2026-07-28 校準（一次對 9 個真實專案的誤報，含 Figma 官方與 ★18k 的
# oh-my-posh）：初版把「零寬 + BOM + 私有使用區 + 方向標記」通通判為
# CRITICAL，結果抓到的全是正常用途——
#   · U+E000–F8FF 私有使用區 → Nerd Font 圖示。oh-my-posh 是 shell 主題
#     工具，它就是靠這些字元畫圖示的
#   · U+FEFF → BOM。命中點正好在某專案的 csv.ts，處理 Excel CSV 必須用
#   · U+200D → emoji 組合（ZWJ）的必要字元
#   · U+200E/200F → 方向標記，任何 i18n 專案都會用
#
# 真正「你讀到的程式碼 ≠ 實際執行的程式碼」的手法是 Trojan Source
# （CVE-2021-42574），用的是雙向覆寫與隔離字元，沒有正當用途，留 CRITICAL。
BIDI_CHARS = re.compile("[‪-‮⁦-⁩]")

# 零寬字元用於**隱藏文字**，是另一種攻擊，但在原始碼裡太常見（emoji、
# CJK 排版、壓縮過的 JS），全檔掃描必然誤報。因此只在「會被送進模型的
# 文字」裡查——工具描述與代理指令檔——那裡出現零寬字元才真的沒道理。
ZERO_WIDTH = re.compile("[​‌‍⁠-⁤]")

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
            # 零寬字元在**工具描述**裡才是訊號：那是一段給人和模型讀的短文字，
            # 沒有理由需要不可見字元。（整份原始碼掃就會抓到 emoji 與壓縮 JS）
            zw = ZERO_WIDTH.search(body)
            if zw and ("zw", "") not in seen:
                seen.add(("zw", ""))
                out.append(Finding(
                    "工具描述投毒", MEDIUM, "工具描述含零寬字元",
                    "描述裡有看不見的字元。emoji 組合會用到零寬連接字元，"
                    "所以不一定是惡意；但它也是把指令藏進描述、讓人讀不出來的"
                    "手法。請確認那個位置為什麼需要它。",
                    evidence=f"{path}｜U+{ord(zw.group()):04X}｜"
                             f"「{' '.join(body.split())[:90]}」"))
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

        # 全檔只掃 bidi 覆寫。零寬字元改在下方的「工具描述」層級查——
        # 那裡出現才沒有正當理由，掃整份原始碼只會抓到 emoji 與壓縮過的 JS。
        for hit in BIDI_CHARS.finditer(text):
            out.append(Finding(
                "工具描述投毒", CRITICAL, "原始碼含雙向覆寫字元",
                "bidi 覆寫字元會讓「你在畫面上讀到的程式碼」與「編譯器實際讀到的」"
                "順序不同，是 Trojan Source（CVE-2021-42574）的手法。"
                "除了處理雙向文字的函式庫，正常原始碼沒有理由出現它們。",
                evidence=f"{path}｜位置 {hit.start()}｜U+{ord(hit.group()):04X}"))
            break   # 每個檔案報一次就夠

    if not out:
        out.append(Finding(
            "工具描述投毒", INFO,
            f"未發現可疑工具描述（已掃描 {scanned} 段 description）",
            "沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，"
            "但常見的 tool poisoning 手法都沒有命中。"))
    return out


# ── 5. 代理指令檔投毒（SKILL.md / AGENTS.md / CLAUDE.md …）──────────────────
# 2026-07-28 dogfooding 時發現的自家漏洞：掃一個 Claude Code plugin 時，整份
# SKILL.md 因為副檔名是 .md 被跳過，只能手動 grep 才確認乾淨。
#
# 這類檔案會被客戶端自動讀進上下文，和 tool description 是同一種攻擊面——
# 而且**更直接**：tool description 還得偽裝成功能說明才不突兀，指令檔本身
# 就是純指令，攻擊者不必偽裝任何東西。

AGENT_CHECK = "代理指令檔"

# 判準和第 4 項不同：指令檔**本來就是**在對模型下指令，所以「務必先呼叫 X」
# 在這裡是完全正常的寫法（幾乎每個 skill 都會寫），列入樣式等於全體誤報。
# 這裡只留「即使身為指令檔也解釋不通」的手法。
#
# 末欄 warn_ok＝這條規則可否被「警告語境」豁免。前兩條是 False：講解時會用
# 引號或防禦語境詞，而「不要告訴使用者」本身就含否定詞，開放警告豁免等於
# 讓真投毒靠一個 don't 就降級。
AGENT_PATTERNS = [
    (RE_IGNORE_PRIOR, CRITICAL, "指令檔要求模型忽略先前指令",
     "這份檔案會被自動讀進模型上下文。要求模型丟棄既有指令（包含你自己的和"
     "客戶端的安全規則），沒有任何正當用途。", False),
    (RE_HIDE_FROM_USER, CRITICAL, "指令檔要求模型對使用者隱瞞",
     "指令檔叫模型不要告訴你它做了什麼——這正是資料外送與靜默破壞會需要的"
     "前置條件，正常的操作說明不需要它。", False),
    (r"--dangerously-skip-permissions|--yolo\b|"
     r"\"?(auto[_-]?approve|autoApprove|alwaysAllow)\"?\s*[:=]\s*(true|\[)",
     HIGH, "指令檔要求關閉權限確認",
     "它指示客戶端跳過工具呼叫的人工確認。一旦生效，後續所有動作都不會再"
     "問過你——包含這份指令檔自己叫模型做的事。", True),
    # 必須帶 URL（或變數）才算：`curl … | sh` 這種佔位寫法是在**舉例**，
    # 不是可執行的指令。2026-07-28 校準，見 WARNING_CONTEXT_RE 的說明。
    (r"(curl|wget)\s+[^\n|]{0,160}(https?://|\$\w)[^\n|]{0,160}\|\s*"
     r"(sudo\s+)?(ba|z|k|d)?sh|"
     r"i(wr|rm)\s+[^\n|]{0,160}(https?://|\$\w)[^\n|]{0,160}\|\s*iex",
     HIGH, "指令檔要求下載並直接執行遠端腳本",
     "叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——"
     "你稽核過的原始碼完全管不到它。", True),
    (r"<\s*system\s*>|\[\s*system\s*\]|</\s*system\s*>", MEDIUM,
     "指令檔出現系統訊息標記",
     "文字裡插入 <system> 這類標記，常見目的是讓自己的內容看起來像是"
     "客戶端下達的系統指令，藉此取得更高的服從度。", True),
    (r"\.ssh/|id_rsa|BEGIN\s+(RSA|OPENSSH)\s+PRIVATE\s+KEY|私鑰", MEDIUM,
     "指令檔提及金鑰或 SSH 路徑",
     "若這份指令的主題本來就是金鑰管理屬正常；否則要問：一份操作說明"
     "為什麼需要讓模型知道私鑰放在哪裡。", True),
]

# 刻意**不做**的一條規則：「要求不經詢問就執行」。
# 2026-07-28 對 DesktopCommanderMCP 實測時，它命中的是
# 「…reconstruct the work without asking the user to recap」——語意完全良性。
# 這類措辭在正常 skill 裡到處都是，自然語言層面分不出「不問就刪檔」和
# 「不用再請使用者複述」。真正危險的自動核准已由上面的具名旗標涵蓋，
# 那條精準得多。訊號弱到只能製造噪音的規則，不如不要。

# 安全類專案的文件會**引述**攻擊手法（本專案自己的 README 就是最好的例子），
# 一律判 CRITICAL 等於把防禦方當成攻擊方。命中防禦／說明語境時降一級並註明。
#
# 代價很明確：攻擊者可以在投毒段落裡加一句「以下為範例」來規避降級門檻。
# 仍然這樣做，是因為降級後該項**依舊會出現在報告裡**由人判讀，而對真實專案
# 的不實指控是收不回來的——這個取捨和第 4 項的校準一致。
DEFENSIVE_CONTEXT_RE = re.compile(
    r"prompt\s*injection|jailbreak|red[\s-]*team|malicious|attack|exploit|"
    r"vulnerab|threat\s*model|for\s+example|e\.g\.|"
    r"注入|投毒|惡意|攻擊|紅隊|弱點|漏洞|偵測|防禦|稽核|手法|樣式|"
    r"例如|範例|示例|示範", re.I)

# 第三種豁免訊號：**警告**語境。
# 2026-07-28 實測誤報：DesktopCommanderMCP 的 terminal skill 寫著
# 「Be careful with anything that pipes a downloaded script straight into a
# shell (`curl ... | sh`) — that's untrusted code execution; confirm first」——
# 一份在教模型「別這樣做」的安全指引，被判成要求下載執行遠端腳本。
# 只看命中點附近，不看整段：長文件裡出現一次 "avoid" 就全體豁免太寬。
WARNING_CONTEXT_RE = re.compile(
    r"be\s+careful|caution|never\b|avoid|do\s*not\b|don'?t\b|refuse|"
    r"untrusted|unsafe|dangerous|risky|confirm\s+first|ask\s+first|"
    r"require[sd]?\s+(approval|confirmation)|"
    r"不要|勿|避免|禁止|危險|不安全|風險|先確認|需(要)?確認", re.I)
WARNING_WINDOW = 160        # 命中點前後各看這麼多字

# 比關鍵字更結構化的一個訊號：**引述**幾乎都被引號包住（安全文件寫
# 「ignore all previous instructions」時是在指名一種手法），**指示**則是裸句。
# 這條比字面關鍵字難規避——把指令放進引號，對模型的指示力本身就會下降。
#
# 反引號與括號**刻意排除**：markdown 的 `code` 是程式碼標記不是引述，被
# 反引號包住的 `curl … | sh` 反而更像是真的要執行它。初版把反引號算進來，
# 結果兩個真投毒樣本被降級——降級訊號選錯，等於替攻擊者做了規避。
QUOTE_OPEN, QUOTE_CLOSE = "「『“‘《\"'", "」』”’》\"'"

_DOWNGRADE = {CRITICAL: MEDIUM, HIGH: MEDIUM, MEDIUM: LOW, LOW: LOW}


MAX_AGENT_FINDINGS = 12     # 同型問題散落幾十個 skill 時，不要洗掉整份報告


def _is_quoted(block: str, start: int, end: int) -> bool:
    """命中片段是否被同一行的引號包住（→ 傾向為引述而非指示）。"""
    line_start = block.rfind("\n", 0, start) + 1
    line_end = block.find("\n", end)
    line_end = len(block) if line_end < 0 else line_end
    before, after = block[line_start:start], block[end:line_end]
    return (any(c in before for c in QUOTE_OPEN)
            and any(c in after for c in QUOTE_CLOSE))


def _excused(block: str, m: re.Match, warn_ok: bool) -> bool:
    """這次命中比較像「引述／警告」而不是「指示」嗎？

    語境一律取命中片段**以外**的文字。否則會出現這種笑話：
    `--dangerously-skip-permissions` 因為旗標名稱裡有 "dangerous"，
    被自己判定成一句安全警告而降級。
    """
    s, e = m.span()
    if _is_quoted(block, s, e):
        return True
    if DEFENSIVE_CONTEXT_RE.search(block[:s] + "\n" + block[e:]):
        return True
    if not warn_ok:
        return False
    near = (block[max(0, s - WARNING_WINDOW):s] + "\n"
            + block[e:e + WARNING_WINDOW])
    return bool(WARNING_CONTEXT_RE.search(near))


def _snippet(block: str, start: int, end: int, pad: int = 70) -> str:
    """取命中片段**周圍**的文字當證據。

    早期版本秀段落開頭，長段落一路截到看不見命中點——讀者無從判斷對錯，
    等於逼人重新自己找一次。
    """
    a, b_ = max(0, start - pad), min(len(block), end + pad)
    body = " ".join(block[a:b_].split())
    return ("…" if a > 0 else "") + body + ("…" if b_ < len(block) else "")


def _blocks(text: str):
    """把指令檔切成段落逐段判斷。

    整檔當成一段會讓「同段命中多項」失去意義，證據也會指不到位置。
    """
    for raw in re.split(r"\n\s*\n", text):
        s = raw.strip()
        if s:
            yield s


def check_agent_instructions(b: RepoBundle) -> list[Finding]:
    targets = [(p, t, k) for p, t in b.files.items() if (k := agentfiles.kind(p))]
    if not targets:
        return [Finding(
            AGENT_CHECK, INFO, "沒有代理指令檔",
            "這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類"
            "會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。")]

    # (嚴重度, 標題, 說明, 命中片段) -> 出現在哪些檔案。
    # 用命中片段當去重鍵，因為 plugin 專案常把同一份 SKILL.md 複製到
    # plugins/claude/、plugins/cursor/、根目錄——同一句話報三次是雜訊不是證據。
    hits: dict[tuple[str, str, str, str], list[str]] = {}

    for path, text, _k in sorted(targets):
        # 指令檔本身就是一段要送進模型的說明文字，不是程式碼——這裡出現
        # 零寬或 bidi 字元都沒有正當理由，兩者都留在高風險。
        for pat, sev, label in ((BIDI_CHARS, CRITICAL, "雙向覆寫字元"),
                                (ZERO_WIDTH, HIGH, "零寬字元")):
            hit = pat.search(text)
            if not hit:
                continue
            key = (sev, f"指令檔含{label}",
                   "這類字元可讓「你在 GitHub 上讀到的內容」與「模型實際收到的"
                   "指令」不一致。一份給人讀的說明文件沒有理由用到它們。",
                   f"位置 {hit.start()}｜U+{ord(hit.group()):04X}")
            hits.setdefault(key, []).append(path)

        for block in _blocks(text):
            for pat, sev, label, why, warn_ok in AGENT_PATTERNS:
                m = re.search(pat, block, re.I)
                if not m:
                    continue
                if _excused(block, m, warn_ok):
                    sev, label = _DOWNGRADE[sev], f"{label}（疑為引述或警告）"
                    why += ("\n\n這段文字帶有講解或警告的語氣（被引號包住、"
                            "或鄰近出現「不要／避免／untrusted」之類的字眼），"
                            "因此已降級——安全類專案的文件經常引述這些寫法，"
                            "把防禦方指控成攻擊方是更難挽回的錯誤。"
                            "請確認它確實是在說明，而不是在指示。")
                hits.setdefault((sev, label, why, _snippet(block, *m.span())),
                                []).append(path)

    out: list[Finding] = []
    for (sev, label, why, snippet), paths in hits.items():
        ev = f"{paths[0]}｜「{snippet}」"
        if len(paths) > 1:
            ev += f"（另 {len(paths) - 1} 個檔案有相同內容）"
        out.append(Finding(AGENT_CHECK, sev, label, why, evidence=ev))

    if len(out) > MAX_AGENT_FINDINGS:
        rest = len(out) - MAX_AGENT_FINDINGS
        out = out[:MAX_AGENT_FINDINGS]
        out.append(Finding(
            AGENT_CHECK, INFO, f"另有 {rest} 項同類發現未列出",
            "同型問題散落在多個指令檔中，此處只列前面幾項；"
            "請直接檢視這些檔案本身。"))

    listed = "、".join(f"{p}（{k}）" for p, _t, k in sorted(targets)[:6])
    out.append(Finding(
        AGENT_CHECK, INFO, f"已掃描 {len(targets)} 個代理指令檔",
        "這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字"
        "讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。",
        evidence=listed + ("…" if len(targets) > 6 else "")))
    return out


# ── 6. 維護活躍度 ───────────────────────────────────────────────────────────

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
              check_tool_poisoning, check_agent_instructions, check_maintenance)


def run_all(b: RepoBundle) -> list[Finding]:
    findings: list[Finding] = []
    for fn in ALL_CHECKS:
        try:
            findings.extend(fn(b))
        except Exception as e:      # 單項壞掉不該讓整份報告掛掉
            findings.append(Finding(fn.__name__, INFO, "此項檢查執行失敗",
                                    f"{type(e).__name__}: {e}"))
    return findings
