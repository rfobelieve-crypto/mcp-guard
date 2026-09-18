# -*- coding: utf-8 -*-
"""把使用者「手上真正有的東西」正規化成可稽核的目標。

`fetch.parse_target` 接受的是乾淨的 `owner/repo`、GitHub 網址或 `npm:套件名`。
但使用者手上真正有的，通常是這些：

    npx -y @modelcontextprotocol/server-filesystem /path
    uvx some-mcp-server
    {"mcpServers": {"fs": {"command": "npx", "args": ["-y", "@scope/pkg"]}}}

要求使用者自己轉換，等於在漏斗最上緣設一道關卡。這個模組負責把上面
那些東西變成 parse_target 看得懂的字串。

刻意獨立成一個模組而不是改 parse_target：稽核引擎的既有行為一個字都不動，
這裡只做「輸入前的翻譯」，翻不出來就原樣回傳，交給既有邏輯處理。
"""
from __future__ import annotations

import json
import re

# npx / uvx / pnpm dlx 這類「執行器」旗標，不是套件名
_RUNNER_FLAGS = {
    "-y", "--yes", "-q", "--quiet", "-p", "--package", "--silent",
    "-f", "--force", "--no-install", "-g", "--global",
}
# 會出現在安裝／執行指令開頭的字，本身不是套件名
_RUNNERS = {
    "npx", "uvx", "pnpx", "bunx", "npm", "pnpm", "yarn", "bun",
    "pip", "pip3", "pipx", "uv", "dlx", "exec", "install", "add", "run",
}


def _strip_version(pkg: str) -> str:
    """去掉版本後綴，但保留 scope 前面的 @。

    `@scope/pkg@1.2.3` → `@scope/pkg`
    `pkg@latest`       → `pkg`
    """
    if pkg.startswith("@"):
        # scope 的 @ 在最前面，版本的 @ 在第一個 / 之後
        head, sep, tail = pkg.partition("/")
        if not sep:
            return pkg
        return f"{head}/{tail.split('@', 1)[0]}"
    return pkg.split("@", 1)[0]


def _from_argv(tokens: list[str]) -> str:
    """從一串指令 token 裡挑出套件名。挑不到回空字串。"""
    for tok in tokens:
        t = tok.strip().strip(",")
        if not t or t in _RUNNER_FLAGS or t.lower() in _RUNNERS:
            continue
        if t.startswith("-"):
            continue
        # 路徑參數（/Users/…、./x、C:\…）不是套件名
        if t.startswith(("/", ".", "~")) or re.match(r"^[A-Za-z]:[\\/]", t):
            continue
        # 環境變數指派（FOO=bar）不是套件名
        if "=" in t and not t.startswith("@"):
            continue
        return _strip_version(t)
    return ""


def _from_config(obj) -> str:
    """從 MCP 客戶端設定檔（或其片段）裡挑出第一個可稽核的目標。

    涵蓋 Claude Desktop 的 `mcpServers`、以及直接貼單一 server 物件的情況。
    """
    if isinstance(obj, dict):
        # 直接是一個 server 定義
        if "command" in obj or "args" in obj:
            args = obj.get("args") or []
            if isinstance(args, list):
                hit = _from_argv([str(a) for a in args])
                if hit:
                    return hit
            cmd = obj.get("command")
            if isinstance(cmd, str) and cmd.lower() not in _RUNNERS:
                return _strip_version(cmd)
        for key in ("mcpServers", "servers", "mcp"):
            if key in obj:
                hit = _from_config(obj[key])
                if hit:
                    return hit
        for value in obj.values():
            hit = _from_config(value)
            if hit:
                return hit
    elif isinstance(obj, list):
        for item in obj:
            hit = _from_config(item)
            if hit:
                return hit
    return ""


def normalize(raw: str) -> str:
    """把使用者輸入轉成 parse_target 看得懂的字串。

    翻譯不出來就原樣回傳——讓既有邏輯去處理，而不是在這裡擅自否決。
    """
    s = (raw or "").strip()
    if not s:
        return s

    # 已經是乾淨格式就別動它
    if s.startswith("npm:") or "github.com" in s:
        return s

    # 設定檔（或其片段）
    if s.startswith(("{", "[")):
        try:
            hit = _from_config(json.loads(s))
        except json.JSONDecodeError:
            hit = ""
        if hit:
            return f"npm:{hit}" if not _looks_like_slug(hit) else hit
        # JSON 解析失敗時退而求其次：從整段文字裡撈 npx 指令
        s = re.sub(r"[\"',\[\]{}]", " ", s)

    # 安裝／執行指令
    tokens = s.split()
    if len(tokens) > 1 or tokens[0].lower() in _RUNNERS:
        hit = _from_argv(tokens)
        if hit:
            return hit if _looks_like_slug(hit) else f"npm:{hit}"

    return s


def _looks_like_slug(s: str) -> bool:
    """`owner/repo` 形狀，且不是 npm 的 `@scope/pkg`。"""
    return bool(re.fullmatch(r"[\w.-]+/[\w.-]+", s))
