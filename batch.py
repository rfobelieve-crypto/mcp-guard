# -*- coding: utf-8 -*-
"""批次安檢：掃一批 MCP 專案，產出總表 + 個別報告。

用法：
    python batch.py                 # 掃內建名單
    python batch.py 清單.txt         # 一行一個 owner/repo
輸出：
    reports/總表.md      排序後的安檢總表
    reports/<repo>.md    個別完整報告
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp_guard.checks import CRITICAL, HIGH, LOW, MEDIUM, run_all
from mcp_guard.fetch import collect
from mcp_guard.report import render, verdict

OUT = Path(__file__).resolve().parent / "reports"

# 首批名單：實際是 MCP server / 官方工具，且以高星與台港常用場景為主。
# 刻意納入幾個「權限天生就大」的（桌面控制、瀏覽器、資料庫），
# 因為那正是使用者最需要在安裝前看懂的類型。
TARGETS = [
    "modelcontextprotocol/servers",
    "modelcontextprotocol/inspector",
    "modelcontextprotocol/registry",
    "microsoft/playwright-mcp",
    "github/github-mcp-server",
    "googleapis/mcp-toolbox",
    "GLips/Figma-Context-MCP",
    "hangwin/mcp-chrome",
    "wonderwhy-er/DesktopCommanderMCP",
    "CursorTouch/Windows-MCP",
    "idosal/git-mcp",
    "firecrawl/firecrawl-mcp-server",
    "BrowserMCP/mcp",
    "awslabs/mcp",
    "LaurieWired/GhidraMCP",
    "DeusData/codebase-memory-mcp",
    "BeehiveInnovations/pal-mcp-server",
    "PrefectHQ/fastmcp",
]

RANK = {"🔴 不要安裝": 0, "🟡 需人工複核": 1, "🟢 未發現明顯風險": 2}

SYNCED = Path(__file__).resolve().parent / "targets.txt"
REG_META = OUT / "registry_meta.json"


def read_targets(path: Path) -> list[str]:
    """讀名單檔。支援整行註解與行內註解（`owner/repo  # ★1,234`）。"""
    out, seen = [], set()
    for line in path.read_text(encoding="utf-8").splitlines():
        slug = line.split("#", 1)[0].strip()
        if slug and slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def scan_one(slug: str, registry: dict | None = None) -> dict:
    b = collect(slug)
    if registry is not None:
        b.registry = registry
    findings = run_all(b)
    v, why = verdict(findings)
    OUT.mkdir(exist_ok=True)
    safe = slug.replace("/", "__")
    (OUT / f"{safe}.md").write_text(render(b, findings, slug), encoding="utf-8")
    order = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, "INFO": 4}
    return {
        "slug": slug,
        "verdict": v,
        "why": why,
        "desc": (b.meta.get("description") or "") if b.exists else "",
        "stars": b.meta.get("stargazers_count", 0) if b.exists else 0,
        "pushed": (b.meta.get("pushed_at", "") or "")[:10],
        "lang": (b.meta.get("language") or "") if b.exists else "",
        # 發布者身分：驗證到什麼程度，不是安全性評價
        "pub": (b.registry.get("label", "") if b.registry.get("registered")
                else "未登錄 registry"),
        "pub_kind": (b.registry.get("kind", "") if b.registry.get("registered")
                     else "none"),
        "files": len(b.files),
        "crit": sum(f.severity == CRITICAL for f in findings),
        "high": sum(f.severity == HIGH for f in findings),
        "med": sum(f.severity == MEDIUM for f in findings),
        # 投毒欄位涵蓋兩種載體：tool description 與代理指令檔。
        # 對讀者而言兩者是同一件事——「模型讀得到、你讀不到的指令」。
        "poison": sum(f.check in ("工具描述投毒", "代理指令檔")
                      and f.severity == CRITICAL for f in findings),
        "top": next((f.title for f in findings
                     if f.severity in (CRITICAL, HIGH)), "—"),
        # 完整發現供網站展開顯示——結論一定要能一路追到證據
        "findings": [
            {"check": f.check, "severity": f.severity, "title": f.title,
             "detail": f.detail, "evidence": f.evidence}
            for f in sorted(findings, key=lambda x: order.get(x.severity, 9))
        ],
    }


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    # 名單優先序：命令列指定 > 同步產生的 targets.txt > 內建核心名單。
    # 這樣 CI 不必改參數，本地也能隨時退回只掃核心名單。
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else SYNCED
    if path.exists():
        targets = read_targets(path)
        print(f"名單來源：{path.name}（{len(targets)} 個目標）")
    else:
        targets = list(TARGETS)
        print(f"名單來源：內建核心名單（{len(targets)} 個目標）")

    # 發布者身分由 sync_targets.py 從官方 registry 取得，缺檔不影響掃描
    reg_meta = {}
    if REG_META.exists():
        try:
            reg_meta = json.loads(REG_META.read_text(encoding="utf-8")).get(
                "servers", {})
        except (json.JSONDecodeError, OSError):
            pass

    rows, t0 = [], time.time()
    for i, slug in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {slug} …", flush=True)
        try:
            r = scan_one(slug, reg_meta.get(slug))
            rows.append(r)
            print(f"    {r['verdict']}  嚴重{r['crit']} 高{r['high']} "
                  f"中{r['med']}  ({r['files']} 檔)", flush=True)
        except Exception as e:
            print(f"    掃描失敗：{type(e).__name__}: {e}", flush=True)
            traceback.print_exc()

    rows.sort(key=lambda r: (RANK.get(r["verdict"], 9), -r["high"], -r["stars"]))

    md = [
        "# MCP 安檢總表",
        "",
        f"掃描時間：{time.strftime('%Y-%m-%d %H:%M')}　"
        f"對象：{len(rows)} 個專案　耗時 {time.time()-t0:.0f} 秒",
        "",
        "> 這是**靜態稽核**結果：只讀原始碼與公開中繼資料，不執行目標程式。",
        "> 「未發現明顯風險」代表已知樣式沒命中，**不等於安全背書**。",
        "> 權限大不等於惡意——工具型 MCP 本來就需要大權限，重點是你**知情**。",
        "",
        "| 專案 | 結論 | ⭐ | 嚴重 | 高 | 中 | 投毒 | 最主要風險 | 最後更新 |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for r in rows:
        md.append(
            f"| [`{r['slug']}`](https://github.com/{r['slug']}) | {r['verdict']} "
            f"| {r['stars']:,} | {r['crit']} | {r['high']} | {r['med']} "
            f"| {r['poison']} | {r['top']} | {r['pushed']} |")

    md += [
        "",
        "## 怎麼讀這張表",
        "",
        "- **🔴 不要安裝**：出現嚴重問題（倉庫不存在、工具描述投毒、隱藏字元等）。",
        "- **🟡 需人工複核**：有高風險項目——多半是「會開子行程」「會讀寫檔案」，",
        "  對桌面控制、瀏覽器、資料庫類 MCP 屬正常，但你必須知道自己授予了什麼。",
        "- **投毒欄**：工具描述中偵測到可疑指令的數量，**這欄非 0 就要停下來看**。",
        "",
        "個別完整報告見同目錄下 `<owner>__<repo>.md`。",
        "",
        "*由 MCP 安檢（mcp-guard）產生 · 繁體中文*",
    ]
    OUT.mkdir(exist_ok=True)
    (OUT / "總表.md").write_text("\n".join(md), encoding="utf-8")

    # 結構化輸出：網站產生器（site.py）的唯一資料來源
    (OUT / "data.json").write_text(json.dumps({
        "scanned_at": time.strftime("%Y-%m-%d %H:%M"),
        "elapsed_sec": round(time.time() - t0),
        "projects": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n完成：{len(rows)} 個 → reports/總表.md、reports/data.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
