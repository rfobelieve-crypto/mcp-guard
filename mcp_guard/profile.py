# -*- coding: utf-8 -*-
"""用途推斷：這個 MCP「宣稱」自己是做什麼的？

為什麼需要這一層：
單看「會開子行程」毫無區辨度——桌面控制類 MCP 本來就要開 shell，
但一個天氣查詢 MCP 會開 shell 就非常可疑。同一個權限，
放在不同宣稱用途下的意義完全不同。

因此先從公開描述（repo description / topics / README / 套件名）推斷用途，
再據此判斷實際用到的能力是「本份」還是「超出範圍」。

推斷只用**公開自述**，不看實作——這正是重點：
我們要比對的就是「它說它是什麼」vs「它實際要什麼權限」。
"""
from __future__ import annotations

import re

from .fetch import RepoBundle

# 能力代號
EXEC, EVAL_, FS, ENV, NET = "EXEC", "EVAL", "FS", "ENV", "NET"

CAP_ZH = {
    EXEC: "執行外部指令",
    EVAL_: "動態執行程式碼",
    FS: "讀寫本機檔案",
    ENV: "讀取環境變數",
    NET: "連線外部主機",
}

# 用途 → (中文名, 這類用途「本來就需要」的能力)
# 排在前面的優先命中，因此specific 的放前面、泛用的放後面。
PROFILES: list[tuple[str, str, str, set[str]]] = [
    ("desktop", r"desktop\s*command|computer[- ]use|windows[- ]mcp|"
                r"terminal|shell|command\s*line|automat\w* (the )?(pc|computer)|"
                r"控制電腦|桌面控制",
     "桌面／終端控制", {EXEC, FS, ENV, NET}),

    ("browser", r"browser|playwright|puppeteer|chrome|firefox|webdriver|"
                r"crawl|scrap\w+|瀏覽器",
     "瀏覽器／網頁自動化", {EXEC, FS, ENV, NET}),

    ("devtool", r"\bsdk\b|framework|\blibrary\b|inspector|registry|toolbox|"
                r"boilerplate|scaffold|build (mcp|servers)|開發框架",
     "開發框架／工具鏈", {EXEC, FS, ENV, NET}),

    ("code", r"\bgit\b|repositor|codebase|source code|static analys|"
             r"decompil|ghidra|ide\b|程式碼",
     "程式碼／版控工具", {EXEC, FS, ENV, NET}),

    ("filesystem", r"file ?system|read (and )?write files|directory|"
                   r"local files|檔案系統",
     "檔案系統存取", {FS, ENV, NET}),

    ("database", r"\bsql\b|postgres|mysql|sqlite|mongo|database|資料庫",
     "資料庫存取", {NET, ENV, FS}),

    ("cloud", r"\baws\b|azure|gcp|google cloud|kubernetes|terraform|雲端",
     "雲端服務串接", {NET, ENV, FS, EXEC}),

    ("api", r"\bapi\b|integration|connector|client for|wrapper|"
            r"github|figma|slack|notion|jira|串接",
     "第三方 API 串接", {NET, ENV}),

    ("docs", r"documentation|knowledge|search|retriev|rag\b|memory|"
             r"文件|知識庫|檢索",
     "文件／知識檢索", {NET, ENV, FS}),
]

DEFAULT_PROFILE = ("general", "一般用途（未能明確判定）", {NET, ENV})


def infer(b: RepoBundle) -> tuple[str, str, set[str]]:
    """回傳 (代號, 中文用途, 預期能力集合)。"""
    parts = [
        b.meta.get("description") or "",
        " ".join(b.meta.get("topics") or []),
        b.slug,
        b.npm_name,
    ]
    # README 只取前段：後面通常是安裝說明與雜項，雜訊多
    for path, text in b.files.items():
        if path.lower() in ("readme.md", "readme_zh-cn.md", "readme.zh.md"):
            parts.append(text[:2000])
    blob = " ".join(parts).lower()

    for code, pattern, zh, caps in PROFILES:
        if re.search(pattern, blob, re.I):
            return code, zh, caps
    return DEFAULT_PROFILE
