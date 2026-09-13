# -*- coding: utf-8 -*-
"""輸入正規化測試。

這一層錯了，使用者連稽核都跑不到——比誤判更早、更致命的失敗點。
樣本刻意用真實世界會出現的字串，不是理想化的乾淨輸入。
"""
from __future__ import annotations

import sys

from mcp_guard.userinput import normalize

# (輸入, 期望輸出, 說明)
CASES = [
    # ── 已經乾淨的格式：一個字都不該動 ──────────────────────────
    ("owner/repo", "owner/repo", "已是 slug"),
    ("https://github.com/owner/repo", "https://github.com/owner/repo", "GitHub 網址"),
    ("npm:some-mcp", "npm:some-mcp", "已標明 npm"),

    # ── 安裝／執行指令：使用者最常直接複製的東西 ────────────────
    ("npx -y @modelcontextprotocol/server-filesystem",
     "npm:@modelcontextprotocol/server-filesystem", "npx + -y 旗標"),
    ("npx @scope/pkg", "npm:@scope/pkg", "npx 無旗標"),
    ("npx -y @scope/pkg@1.2.3", "npm:@scope/pkg", "帶版本的 scoped 套件"),
    ("npx some-mcp@latest", "npm:some-mcp", "帶 dist-tag"),
    ("npm install some-mcp", "npm:some-mcp", "npm install"),
    ("pnpm dlx @scope/pkg", "npm:@scope/pkg", "pnpm dlx"),
    ("uvx some-python-mcp", "npm:some-python-mcp", "uvx（Python 執行器）"),
    ("pip install some-mcp", "npm:some-mcp", "pip install"),

    # ── 帶路徑參數：路徑不該被當成套件名 ────────────────────────
    ("npx -y @modelcontextprotocol/server-filesystem /Users/me/docs",
     "npm:@modelcontextprotocol/server-filesystem", "套件名後面接路徑"),
    ("npx -y @scope/pkg ./local/dir", "npm:@scope/pkg", "相對路徑參數"),

    # ── 設定檔片段：使用者從 claude_desktop_config.json 直接貼 ──
    ('{"mcpServers": {"fs": {"command": "npx", '
     '"args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]}}}',
     "npm:@modelcontextprotocol/server-filesystem", "完整 mcpServers 設定"),
    ('{"command": "npx", "args": ["-y", "@scope/pkg"]}',
     "npm:@scope/pkg", "單一 server 物件"),

    # ── 翻不出來的就原樣回傳，交給既有邏輯 ──────────────────────
    ("some-bare-package", "some-bare-package", "裸套件名維持原樣"),
]


def main() -> int:
    bad = []
    for raw, want, why in CASES:
        got = normalize(raw)
        if got != want:
            bad.append((why, raw, want, got))
            print(f"  ❌ {why}\n     輸入：{raw}\n     期望：{want}\n     實得：{got}")
        else:
            print(f"  ✅ {why}")

    print()
    if bad:
        print(f"輸入正規化：{len(bad)} / {len(CASES)} 項未通過")
        return 1
    print(f"輸入正規化：{len(CASES)} 項全數通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
