# -*- coding: utf-8 -*-
"""隨選掃描 API：`GET /api/scan?target=...`

存在的理由：官方 registry 上有約 13,800 個 GitHub 專案，網站預先掃過的
只有 178 個。使用者查不到的機率是 98.7%，而那一刻正是他最想知道答案的
時候——他手上拿著安裝指令，正要按下去。

CLI 本來就能查任意專案（`collect()` 是即時抓取，與預掃名單無關），
這支 API 只是把同一條路徑接到網頁上。

刻意的設計：
- 引擎一個字都不改，只是被呼叫。結論與 CLI 逐字相同，可自行複現。
- 抓取失敗（限流、逾時）回 502 而**不是**一份看似乾淨的報告。
  「查不動」與「沒問題」是兩件事，見 tests/test_lookup.py。
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Vercel 會把整個 repo 放進函式的工作目錄，但不保證它在 sys.path 上。
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_guard.checks import run_all                      # noqa: E402
from mcp_guard.fetch import FetchError, collect           # noqa: E402
from mcp_guard.report import verdict                      # noqa: E402
from mcp_guard.userinput import normalize                 # noqa: E402

MAX_TARGET_LEN = 8000     # 夠貼一整份設定檔，又不至於變成任意大的輸入


def scan(raw_target: str) -> dict:
    """跑一次完整稽核，回傳可序列化的結果。"""
    target = normalize(raw_target)
    started = time.time()

    bundle = collect(target)
    findings = run_all(bundle)
    v, why = verdict(findings)
    meta = bundle.meta or {}

    return {
        "ok": True,
        "input": raw_target,
        "target": target,
        "slug": bundle.slug,
        "verdict": v,
        "why": why,
        "desc": meta.get("description") or "",
        "stars": meta.get("stargazers_count", 0),
        "pushed": (meta.get("pushed_at") or "")[:10],
        "license": (meta.get("license") or {}).get("spdx_id") or "",
        "files_scanned": len(bundle.files),
        "notes": bundle.notes,
        "elapsed_ms": int((time.time() - started) * 1000),
        "findings": [
            {
                "check": f.check,
                "severity": f.severity,
                "title": f.title,
                "detail": f.detail,
                "evidence": f.evidence,
            }
            for f in findings
        ],
    }


class handler(BaseHTTPRequestHandler):        # noqa: N801  (Vercel 規定的名稱)
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # 結果會隨專案變動而改變，但同一分鐘內重複查同一個目標沒有意義。
        self.send_header("Cache-Control",
                         "public, max-age=60, s-maxage=300")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:                 # noqa: N802  (BaseHTTPRequestHandler)
        params = parse_qs(urlparse(self.path).query)
        raw = (params.get("target") or [""])[0].strip()

        if not raw:
            self._send(400, {"ok": False, "error": "請提供 target 參數。",
                             "hint": "例如 /api/scan?target=owner/repo"})
            return
        if len(raw) > MAX_TARGET_LEN:
            self._send(413, {"ok": False,
                             "error": f"輸入過長（上限 {MAX_TARGET_LEN} 字元）。"})
            return

        try:
            self._send(200, scan(raw))
        except FetchError as e:
            # 抓取失敗不是「沒問題」，也不是「有問題」——不給結論才是誠實的。
            self._send(502, {"ok": False, "error": str(e), "input": raw})
        except Exception:                                   # noqa: BLE001
            traceback.print_exc()
            self._send(500, {"ok": False,
                             "error": "稽核過程發生未預期的錯誤。",
                             "input": raw})

    def do_POST(self) -> None:                # noqa: N802
        """讓使用者可以直接 POST 一整份設定檔，不必塞進網址。"""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_TARGET_LEN:
            self._send(400, {"ok": False, "error": "請在 body 提供要稽核的內容。"})
            return

        raw = self.rfile.read(length).decode("utf-8", "replace").strip()
        ctype = (self.headers.get("Content-Type") or "").lower()
        if "application/json" in ctype:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict) and "target" in parsed:
                    raw = str(parsed["target"])
            except json.JSONDecodeError:
                pass    # 貼進來的可能就是設定檔本身，交給 normalize 處理

        try:
            self._send(200, scan(raw))
        except FetchError as e:
            self._send(502, {"ok": False, "error": str(e), "input": raw})
        except Exception:                                   # noqa: BLE001
            traceback.print_exc()
            self._send(500, {"ok": False,
                             "error": "稽核過程發生未預期的錯誤。", "input": raw})

    def log_message(self, *args) -> None:     # noqa: D102
        pass          # Vercel 自己有請求日誌，不必再印一份
