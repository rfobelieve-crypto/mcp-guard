# -*- coding: utf-8 -*-
"""API 路由測試。

`vercel.json` 的 `cleanUrls` + `trailingSlash` + `rewrites` 三者相加，
決定了 serverless function 實際會收到什麼路徑。這一層錯掉的症狀是
**每個 /api/* 都回 404**——而且在本機完全看不出來，只有部署後才會發現。

main 上有三個 commit 專門在修這件事（function 不能叫 index、rewrite 目的地
要跟著 cleanUrls 改、source 要補尾斜線變體），代表它容易改壞且靜默失敗。
所以把預期行為鎖在測試裡。

Vercel 的處理順序：

    1. trailingSlash:true  /api/scan       → 轉址 /api/scan/
    2. rewrites            /api/scan/      → /api/rpc/?__path=scan
    3. cleanUrls           /api/rpc/       → function api/rpc.py

也就是說 function 收到的 self.path 是第 2 步的產物，原始子路徑在
`__path` 查詢參數裡。`_route()` 的工作就是把它還原回 /api/scan。
"""
from __future__ import annotations

import io
import json
import sys

sys.path.insert(0, ".")

from mcp_guard import fetch                    # noqa: E402
import api.rpc as rpc                          # noqa: E402

# (function 收到的路徑, 期望還原成, 說明)
ROUTE_CASES = [
    ("/api/rpc/?__path=scan&target=o%2Fr", "/api/scan",
     "經 rewrite——正式環境最可能的形狀"),
    ("/api/rpc?__path=scan&target=o%2Fr", "/api/scan",
     "經 rewrite 但沒有尾斜線"),
    ("/api/scan?target=o%2Fr", "/api/scan",
     "rewrite 未生效、原路徑直達（本機開發會是這種）"),
    ("/api/scan/?target=o%2Fr", "/api/scan",
     "原路徑帶尾斜線"),
    ("/api/rpc/?__path=auth/callback&code=x", "/api/auth/callback",
     "巢狀子路徑不能被截斷——登入流程靠它"),
    ("/api/rpc/?__path=me", "/api/me",
     "既有路由不受影響"),
]


def _fake_transport():
    """假的 GitHub 傳輸層：存在的 repo 回 meta，含 ghost 的回 404。"""
    fetch._gh = lambda a: (
        (0, json.dumps({"description": "demo", "stargazers_count": 9,
                        "pushed_at": "2026-08-01T00:00:00Z", "size": 40,
                        "created_at": "2024-01-01T00:00:00Z"}).encode(), "")
        if a[1].startswith("repos/") and "ghost" not in a[1]
        else (1, b"", "gh: Not Found (HTTP 404)"))
    fetch.fetch_source = lambda s: {}
    fetch.fetch_npm = lambda n: {}
    fetch.fetch_pypi = lambda n: {}


def _call(path: str) -> tuple[int, dict]:
    """跑一次 do_GET，回傳 (狀態碼, 解析後的 JSON)。"""
    state = {"code": None}
    h = object.__new__(rpc.handler)
    h.path = path
    h.headers = {}
    h.wfile = io.BytesIO()
    h.send_response = lambda c, *a: state.__setitem__("code", c)
    h.send_header = lambda *a: None
    h.end_headers = lambda: None
    rpc.handler.do_GET(h)
    try:
        return state["code"], json.loads(h.wfile.getvalue().decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return state["code"], {}


# (路徑, 期望狀態碼, 檢查函式, 說明)
SCAN_CASES = [
    ("/api/rpc/?__path=scan&target=octo%2Ftool", 200,
     lambda d: d.get("ok") and d.get("slug") == "octo/tool",
     "經 rewrite 的正常掃描"),
    ("/api/rpc/?__path=scan&target=npx+-y+%40scope%2Fpkg", 200,
     lambda d: d.get("target") == "npm:@scope/pkg",
     "安裝指令會先過 userinput 正規化"),
    ("/api/rpc/?__path=scan", 400,
     lambda d: "target" in (d.get("error") or ""),
     "缺 target 要回 400 而不是當掉"),
    ("/api/rpc/?__path=nope", 404,
     lambda d: bool(d.get("error")),
     "未知路由回 404"),
]


def main() -> int:
    bad = 0

    print("── _route() 還原原始路徑 ──")
    for path, want, why in ROUTE_CASES:
        h = object.__new__(rpc.handler)
        h.path = path
        got = h._route()
        ok = got == want
        bad += not ok
        print(f"  {'✅' if ok else '❌'} {why}")
        if not ok:
            print(f"      收到 {path}\n      解析 → {got}（期望 {want}）")

    print("\n── /api/scan 端到端 ──")
    _fake_transport()
    for path, want_code, check, why in SCAN_CASES:
        code, data = _call(path)
        ok = code == want_code and check(data)
        bad += not ok
        print(f"  {'✅' if ok else '❌'} {why}")
        if not ok:
            print(f"      HTTP {code}（期望 {want_code}）  {data}")

    total = len(ROUTE_CASES) + len(SCAN_CASES)
    print()
    if bad:
        print(f"API 路由：{bad} / {total} 項未通過")
        return 1
    print(f"API 路由：{total} 項全數通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
