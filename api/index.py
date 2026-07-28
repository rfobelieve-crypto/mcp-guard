# -*- coding: utf-8 -*-
"""網站後端:GitHub OAuth 登入 + 提交掃描請求。單一 function 處理所有 /api/*。

設計立場與 CLI 工具一致:**零第三方相依**——只用標準函式庫。
一個安全稽核網站的後端不該反過來擴大自己的供應鏈。

路由(vercel.json 把 /api/* 全部改寫到這裡):

    GET  /api/auth/login     → 轉往 GitHub 授權頁(帶 state 防 CSRF)
    GET  /api/auth/callback  → 換 token、查身分、簽發 session cookie
    GET  /api/auth/logout    → 清除 session
    GET  /api/me             → 目前登入者(未登入回 401)
    POST /api/submit         → 提交「請掃描這個 MCP」→ 開 GitHub issue

Session 是 HMAC-SHA256 簽名的 cookie(HttpOnly / Secure / SameSite=Lax),
不落資料庫——這個站沒有需要伺服器端保存的使用者狀態,收藏清單存在
使用者自己的瀏覽器(localStorage),這也是最誠實的隱私設計:我們拿不到
就不必解釋怎麼保管。

需要的環境變數(Vercel 專案設定):

    GITHUB_CLIENT_ID      GitHub OAuth App 的 Client ID
    GITHUB_CLIENT_SECRET  GitHub OAuth App 的 Client Secret
    SESSION_SECRET        簽 cookie 的隨機字串(openssl rand -hex 32)
    GITHUB_ISSUE_TOKEN    (選)開 issue 用的 fine-grained PAT,只需
                          目標 repo 的 Issues: Read and write
    ISSUE_REPO            (選)接收掃描請求的 repo,預設本專案
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

SESSION_COOKIE = "mg_session"
STATE_COOKIE = "mg_state"
SESSION_TTL = 60 * 60 * 24 * 30          # 30 天
DEFAULT_ORIGIN = "https://mcp-guard-iota.vercel.app"
DEFAULT_ISSUE_REPO = "rfobelieve-crypto/mcp-guard"
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]{1,80}/[A-Za-z0-9_.-]{1,120}$")


def env(k: str, default: str = "") -> str:
    return os.environ.get(k, default).strip()


# ── session cookie:payload.sig,HMAC-SHA256 ─────────────────────────────

def b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def sign(payload: str, secret: str) -> str:
    return b64e(hmac.new(secret.encode(), payload.encode(),
                         hashlib.sha256).digest())


def make_session(user: dict, secret: str) -> str:
    now = int(time.time())
    payload = b64e(json.dumps({
        "login": user.get("login", ""),
        "name": user.get("name") or "",
        "avatar": user.get("avatar_url", ""),
        "iat": now, "exp": now + SESSION_TTL,
    }, separators=(",", ":")).encode())
    return f"{payload}.{sign(payload, secret)}"


def read_session(cookie_val: str, secret: str) -> dict | None:
    if not cookie_val or "." not in cookie_val or not secret:
        return None
    payload, sig = cookie_val.rsplit(".", 1)
    if not hmac.compare_digest(sign(payload, secret), sig):
        return None
    try:
        data = json.loads(b64d(payload))
    except Exception:
        return None
    if not isinstance(data, dict) or data.get("exp", 0) < time.time():
        return None
    return data


# ── HTTP 小工具 ──────────────────────────────────────────────────────────

def gh_api(url: str, data: dict | None = None, token: str = "",
           accept: str = "application/vnd.github+json") -> dict:
    """對 GitHub 的請求。逾時給短,失敗擲例外由呼叫端轉成使用者訊息。"""
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method="POST" if body else "GET")
    req.add_header("Accept", accept)
    req.add_header("User-Agent", "mcp-guard-site")
    if body:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def parse_cookies(header: str) -> dict:
    out = {}
    for part in (header or "").split(";"):
        if "=" in part:
            k, _, v = part.strip().partition("=")
            out[k] = v
    return out


class handler(BaseHTTPRequestHandler):
    # ── 基礎回應 ────────────────────────────────────────────────

    def _origin(self) -> str:
        """回這個部署自己的 origin。只信任 Vercel 平台網域與正式網域,
        不直接回聲 Host header——那是可偽造的。"""
        host = self.headers.get("x-forwarded-host") or self.headers.get("host") or ""
        host = host.split(",")[0].strip().lower()
        cfg = env("SITE_ORIGIN", DEFAULT_ORIGIN)
        allowed = {urllib.parse.urlsplit(cfg).netloc, "localhost:3000"}
        if host in allowed or host.endswith(".vercel.app"):
            scheme = "http" if host.startswith("localhost") else "https"
            return f"{scheme}://{host}"
        return cfg

    def _json(self, code: int, obj: dict, cookies: list[str] = ()) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        for c in cookies:
            self.send_header("Set-Cookie", c)
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, to: str, cookies: list[str] = ()) -> None:
        self.send_response(302)
        self.send_header("Location", to)
        self.send_header("Cache-Control", "no-store")
        for c in cookies:
            self.send_header("Set-Cookie", c)
        self.end_headers()

    def _cookie(self, name: str, value: str, max_age: int) -> str:
        secure = "" if self._origin().startswith("http://localhost") else " Secure;"
        return (f"{name}={value}; Path=/; Max-Age={max_age};"
                f" HttpOnly;{secure} SameSite=Lax")

    def _user(self) -> dict | None:
        cookies = parse_cookies(self.headers.get("cookie", ""))
        return read_session(cookies.get(SESSION_COOKIE, ""), env("SESSION_SECRET"))

    def _route(self) -> str:
        s = urllib.parse.urlsplit(self.path)
        path = s.path.rstrip("/")
        # vercel.json 的 rewrite 會把原始子路徑放進 __path;多數情況下
        # self.path 就是原始路徑,這裡只是把兩種行為都接住。
        if path in ("/api/index", "/api"):
            sub = (urllib.parse.parse_qs(s.query).get("__path") or [""])[0]
            if sub:
                path = "/api/" + sub.strip("/")
        return path

    # ── GET ─────────────────────────────────────────────────────

    def do_GET(self):  # noqa: N802
        route = self._route()
        try:
            if route == "/api/auth/login":
                return self.auth_login()
            if route == "/api/auth/callback":
                return self.auth_callback()
            if route == "/api/auth/logout":
                return self._redirect(self._origin() + "/",
                                      [self._cookie(SESSION_COOKIE, "", 0)])
            if route == "/api/me":
                # 未設定 auth 時回 503:前端據此完全不畫登入鈕,
                # 而不是擺一顆點了會失敗的按鈕。
                if not env("SESSION_SECRET") or not env("GITHUB_CLIENT_ID"):
                    return self._json(503, {"error": "auth not configured"})
                user = self._user()
                if not user:
                    return self._json(401, {"login": None})
                return self._json(200, {"login": user["login"],
                                        "name": user.get("name", ""),
                                        "avatar": user.get("avatar", "")})
            return self._json(404, {"error": "not found"})
        except urllib.error.URLError:
            return self._json(502, {"error": "github unreachable"})
        except Exception:
            # 不把內部錯誤細節回給瀏覽器
            return self._json(500, {"error": "internal"})

    # ── POST ────────────────────────────────────────────────────

    def do_POST(self):  # noqa: N802
        route = self._route()
        try:
            if route == "/api/auth/logout":
                return self._json(200, {"ok": True},
                                  [self._cookie(SESSION_COOKIE, "", 0)])
            if route == "/api/submit":
                return self.submit()
            return self._json(404, {"error": "not found"})
        except urllib.error.URLError:
            return self._json(502, {"error": "github unreachable"})
        except Exception:
            return self._json(500, {"error": "internal"})

    # ── OAuth ───────────────────────────────────────────────────

    def auth_login(self):
        cid = env("GITHUB_CLIENT_ID")
        if not cid or not env("SESSION_SECRET"):
            return self._json(503, {"error": "auth not configured",
                                    "hint": "設定 GITHUB_CLIENT_ID / "
                                            "GITHUB_CLIENT_SECRET / SESSION_SECRET"})
        state = secrets.token_urlsafe(24)
        q = urllib.parse.urlencode({
            "client_id": cid,
            "redirect_uri": self._origin() + "/api/auth/callback",
            "state": state,
            # 不要任何 scope:我們只需要「你是誰」,不需要碰使用者的任何資源。
            "scope": "",
        })
        return self._redirect(f"https://github.com/login/oauth/authorize?{q}",
                              [self._cookie(STATE_COOKIE, state, 600)])

    def auth_callback(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        code = (qs.get("code") or [""])[0]
        state = (qs.get("state") or [""])[0]
        saved = parse_cookies(self.headers.get("cookie", "")).get(STATE_COOKIE, "")
        if not code or not state or not hmac.compare_digest(state, saved):
            return self._json(400, {"error": "bad state"})
        tok = gh_api("https://github.com/login/oauth/access_token", {
            "client_id": env("GITHUB_CLIENT_ID"),
            "client_secret": env("GITHUB_CLIENT_SECRET"),
            "code": code,
            "redirect_uri": self._origin() + "/api/auth/callback",
        })
        access = tok.get("access_token", "")
        if not access:
            return self._json(400, {"error": "token exchange failed"})
        user = gh_api("https://api.github.com/user", token=access)
        session = make_session(user, env("SESSION_SECRET"))
        return self._redirect(self._origin() + "/", [
            self._cookie(SESSION_COOKIE, session, SESSION_TTL),
            self._cookie(STATE_COOKIE, "", 0),
        ])

    # ── 提交掃描請求 → GitHub issue ─────────────────────────────

    def submit(self):
        user = self._user()
        if not user:
            return self._json(401, {"error": "login required"})
        # SameSite=Lax 之外再驗 Origin:跨站表單貼不進來
        origin = self.headers.get("origin", "")
        if origin and origin != self._origin():
            return self._json(403, {"error": "bad origin"})
        token = env("GITHUB_ISSUE_TOKEN")
        if not token:
            return self._json(503, {"error": "submit not configured",
                                    "hint": "設定 GITHUB_ISSUE_TOKEN"})
        try:
            length = min(int(self.headers.get("content-length", 0)), 8192)
            data = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._json(400, {"error": "bad json"})

        kind = data.get("type")
        repo = (data.get("repo") or "").strip()
        note = (data.get("note") or "").strip()[:1000]
        if kind not in ("scan", "correction") or not REPO_RE.match(repo):
            return self._json(400, {"error": "bad request",
                                    "hint": "repo 需為 owner/repo 格式"})

        issue_repo = env("ISSUE_REPO", DEFAULT_ISSUE_REPO)
        title = (f"[掃描請求] {repo}" if kind == "scan"
                 else f"[回報誤判] {repo}")

        # 查重:同標題已有 open issue 就不重複開,直接回連結。
        # 這同時是最簡單誠實的限流——重複請求不會產生新東西。
        q = urllib.parse.quote(f'repo:{issue_repo} is:issue is:open in:title "{repo}"')
        try:
            found = gh_api(f"https://api.github.com/search/issues?q={q}", token=token)
            for it in found.get("items", []):
                if it.get("title") == title:
                    return self._json(200, {"ok": True, "existing": True,
                                            "url": it.get("html_url", "")})
        except Exception:
            pass  # 查重失敗不擋提交

        body = (f"**提交者**:@{user['login']}(經網站 GitHub 登入)\n"
                f"**類型**:{'請掃描這個 MCP' if kind == 'scan' else '回報稽核結果誤判'}\n"
                f"**專案**:https://github.com/{repo}\n\n"
                + (f"**補充說明**:\n\n{note}\n" if note else ""))
        made = gh_api(f"https://api.github.com/repos/{issue_repo}/issues",
                      {"title": title, "body": body,
                       "labels": ["scan-request" if kind == "scan" else "correction"]},
                      token=token)
        url = made.get("html_url", "")
        if not url:
            return self._json(502, {"error": "issue create failed"})
        return self._json(200, {"ok": True, "url": url})

    def do_HEAD(self):  # noqa: N802 — 健康檢查與爬蟲會發 HEAD
        self.send_response(200)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def log_message(self, *a):  # 安靜:Vercel 自己有請求紀錄
        pass
