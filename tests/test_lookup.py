# -*- coding: utf-8 -*-
"""身分查詢的失敗模式測試。

背景：2026-07-31 在建置隨選掃描 API 時發現，`collect()` 把「查不動」
當成了「不存在」——`gh_json` 對任何非零回應都回 None，包含 403 限流、
429、逾時、5xx。這些全部會走進 check_identity 的 `not b.exists` 分支，
產生 🔴「倉庫與作者帳號都不存在」，證據欄還寫著一個**從未發生過的 404**。

一個好端端的專案，會因為我們這端被限流而被指控成搶註空殼。
這是這個工具最不該犯的錯（見 /trust），所以常駐測試。
"""
from __future__ import annotations

import sys

from mcp_guard import fetch
from mcp_guard.checks import CRITICAL, run_all
from mcp_guard.fetch import FetchError


def _with_fake_gh(responses):
    """把 _gh 換成查表版本。responses: path -> (code, bytes, err)。"""
    def fake(args):
        assert args[0] == "api", args
        return responses.get(args[1], (1, b"", "HTTP 500 unexpected"))
    return fake


def case_ratelimited_repo_is_not_missing() -> tuple[bool, str]:
    """repo 查詢被 403 限流 → 不得宣稱它不存在。"""
    fetch._gh = _with_fake_gh({
        "repos/real/project": (1, b"", "HTTP 403 rate limit exceeded"),
    })
    try:
        fetch.collect("real/project")
    except FetchError as e:
        if "不存在" in str(e) and "無法" not in str(e):
            return False, f"錯誤訊息暗示了不存在：{e}"
        return True, "限流時正確地拒絕產生結論"
    return False, "限流時仍然回傳了一份 bundle（會被判成不存在）"


def case_genuine_404_still_flagged() -> tuple[bool, str]:
    """真的 404 → 仍要照常判 CRITICAL，這是產品的核心價值之一。"""
    fetch._gh = _with_fake_gh({
        "repos/ghost/nothing": (1, b"", "gh: Not Found (HTTP 404)"),
        "users/ghost": (1, b"", "gh: Not Found (HTTP 404)"),
    })
    b = fetch.collect("ghost/nothing")
    if b.exists:
        return False, "404 卻judged為存在"
    findings = run_all(b)
    crit = [f for f in findings if f.severity == CRITICAL]
    if not crit:
        return False, "真正不存在的 repo 沒有被判 CRITICAL（漏報）"
    return True, f"真 404 仍正確判 CRITICAL：{crit[0].title}"


def case_owner_lookup_error_does_not_pick_harsher_wording() -> tuple[bool, str]:
    """repo 確定 404、但作者查不動 → 不得擅自選「連帳號都沒註冊過」那句。"""
    fetch._gh = _with_fake_gh({
        "repos/someone/gone": (1, b"", "gh: Not Found (HTTP 404)"),
        "users/someone": (1, b"", "HTTP 403 rate limit exceeded"),
    })
    try:
        fetch.collect("someone/gone")
    except FetchError:
        return True, "作者查不動時正確地拒絕在兩種措辭中猜一個"
    return False, "作者查不動卻仍產生了結論（可能誤稱帳號未註冊）"


CASES = [
    ("限流不得被當成不存在", case_ratelimited_repo_is_not_missing),
    ("真 404 仍要判 CRITICAL", case_genuine_404_still_flagged),
    ("作者查不動不得選較重的措辭", case_owner_lookup_error_does_not_pick_harsher_wording),
]


def main() -> int:
    original = fetch._gh
    failed = 0
    try:
        for name, fn in CASES:
            ok, detail = fn()
            print(f"  {'✅' if ok else '❌'} {name}：{detail}")
            failed += (not ok)
    finally:
        fetch._gh = original

    print()
    if failed:
        print(f"身分查詢失敗模式：{failed} / {len(CASES)} 項未通過")
        return 1
    print(f"身分查詢失敗模式：{len(CASES)} 項全數通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
