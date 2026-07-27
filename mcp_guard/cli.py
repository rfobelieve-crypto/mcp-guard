# -*- coding: utf-8 -*-
"""MCP 安檢 CLI。

用法：
    python -m mcp_guard owner/repo
    python -m mcp_guard https://github.com/owner/repo
    python -m mcp_guard npm:some-mcp-server
    python -m mcp_guard owner/repo --md 報告.md
"""
from __future__ import annotations

import argparse
import sys

from .checks import CRITICAL, HIGH, run_all
from .fetch import FetchError, collect
from .report import render, render_console


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser(
        prog="mcp-guard", description="MCP 安檢：安裝前先看清楚它要什麼權限")
    ap.add_argument("target", help="owner/repo、GitHub 網址，或 npm:套件名")
    ap.add_argument("--md", metavar="檔案", help="輸出 Markdown 報告到檔案")
    ap.add_argument("--quiet", action="store_true", help="只輸出結論行")
    args = ap.parse_args(argv)

    try:
        bundle = collect(args.target)
    except FetchError as e:
        print(f"抓取失敗：{e}", file=sys.stderr)
        return 2

    findings = run_all(bundle)

    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write(render(bundle, findings, args.target))
        print(f"已寫出報告：{args.md}")

    if not args.quiet:
        print(render_console(bundle, findings, args.target))

    # 退出碼讓它能接進 CI：1 = 有嚴重/高風險
    if any(f.severity == CRITICAL for f in findings):
        return 1
    if sum(f.severity == HIGH for f in findings) >= 2:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
