# -*- coding: utf-8 -*-
"""判定與繁中報告輸出。"""
from __future__ import annotations

from datetime import datetime

from .checks import CRITICAL, HIGH, LOW, MEDIUM, Finding
from .fetch import RepoBundle

ORDER = {CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3, "INFO": 4}
LABEL = {CRITICAL: "🔴 嚴重", HIGH: "🟠 高", MEDIUM: "🟡 中",
         LOW: "🔵 低", "INFO": "⚪ 資訊"}


def verdict(findings: list[Finding]) -> tuple[str, str]:
    """回傳 (結論, 理由)。保守優先：寧可要求人工複核。"""
    n_crit = sum(f.severity == CRITICAL for f in findings)
    n_high = sum(f.severity == HIGH for f in findings)
    if n_crit:
        return "🔴 不要安裝", f"發現 {n_crit} 項嚴重問題，安裝風險無法接受。"
    if n_high >= 2:
        return "🟡 需人工複核", f"發現 {n_high} 項高風險項目，請逐項讀懂後再決定。"
    if n_high == 1:
        return "🟡 需人工複核", "有 1 項高風險項目，確認它是功能必需後才安裝。"
    return "🟢 未發現明顯風險", "常見風險樣式均未命中；仍建議只給最小權限憑證。"


def render(b: RepoBundle, findings: list[Finding], target: str) -> str:
    v, why = verdict(findings)
    m = b.meta
    lines = [
        f"# MCP 安檢報告：{target}",
        "",
        f"> **結論：{v}**　{why}",
        "",
        "| 項目 | 內容 |",
        "|---|---|",
        f"| 稽核對象 | `{b.slug or target}` |",
    ]
    if b.exists:
        lines += [
            f"| 專案說明 | {(m.get('description') or '（無）')[:80]} |",
            f"| 星數 / Fork | ⭐ {m.get('stargazers_count', 0)} / "
            f"{m.get('forks_count', 0)} |",
            f"| 最後更新 | {m.get('pushed_at', '')[:10]} |",
            f"| 授權 | {(m.get('license') or {}).get('name', '無')} |",
        ]
    if b.npm_name:
        lines.append(f"| npm 套件 | `{b.npm_name}`"
                     f"{'（registry 查無）' if not b.npm else ''} |")
    lines += [
        f"| 已掃描檔案 | {len(b.files)} 個 |",
        f"| 檢查時間 | {datetime.now().strftime('%Y-%m-%d %H:%M')} |",
        "",
    ]

    for note in b.notes:
        lines.append(f"> ⚠️ {note}")
    if b.notes:
        lines.append("")

    counts = {s: sum(f.severity == s for f in findings) for s in ORDER}
    lines += [
        "## 風險摘要",
        "",
        "　".join(f"{LABEL[s]} {counts[s]}" for s in ORDER if counts[s]),
        "",
        "## 詳細發現",
        "",
    ]

    for f in sorted(findings, key=lambda x: (ORDER.get(x.severity, 9), x.check)):
        lines.append(f"### {LABEL.get(f.severity, f.severity)}｜[{f.check}] {f.title}")
        lines.append("")
        lines.append(f.detail)
        if f.evidence:
            lines += ["", f"> 證據：`{f.evidence}`"]
        lines.append("")

    lines += [
        "---",
        "",
        "## 這份報告不保證什麼",
        "",
        "- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，",
        "  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。",
        "- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。",
        "- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。",
        "- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。",
        "",
        "*由 MCP 安檢（mcp-guard）產生 · 繁體中文*",
    ]
    return "\n".join(lines)


def render_console(b: RepoBundle, findings: list[Finding], target: str) -> str:
    v, why = verdict(findings)
    out = [f"\n═══ MCP 安檢：{target} ═══", f"結論：{v}  {why}", ""]
    for f in sorted(findings, key=lambda x: (ORDER.get(x.severity, 9), x.check)):
        out.append(f"{LABEL.get(f.severity, f.severity)} [{f.check}] {f.title}")
        if f.evidence:
            out.append(f"    證據：{f.evidence[:150]}")
    out.append("")
    return "\n".join(out)
