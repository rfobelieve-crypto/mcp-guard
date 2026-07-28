# -*- coding: utf-8 -*-
"""代理指令檔（agent instruction files）的辨識規則。

這類檔案會被 AI 客戶端**自動讀進模型上下文**：SKILL.md、AGENTS.md、
CLAUDE.md、.cursorrules……它們和 MCP 的 tool description 同屬攻擊面，
而且更直接——tool description 還得偽裝成功能說明，指令檔本身就是純指令。

抽成獨立模組是為了讓抓取層（fetch）與檢查層（checks）共用同一份定義：
抓不到的檔案永遠掃不到，兩邊清單一旦漂移就是靜默漏報。
"""
from __future__ import annotations

import re

# 檔名（小寫）→ 它會被哪個客戶端自動載入
AGENT_FILE_NAMES = {
    "skill.md": "Agent Skill 指令（SKILL.md）",
    "claude.md": "Claude Code 專案指令（CLAUDE.md）",
    "claude.local.md": "Claude Code 本機指令",
    "agents.md": "Agent 指令（AGENTS.md 慣例）",
    "agent.md": "Agent 指令（AGENT.md）",
    "gemini.md": "Gemini CLI 指令",
    "qwen.md": "Qwen Code 指令",
    "copilot-instructions.md": "GitHub Copilot 指令",
    ".cursorrules": "Cursor 規則",
    ".windsurfrules": "Windsurf 規則",
    ".clinerules": "Cline 規則",
    ".roorules": "Roo Code 規則",
    ".goosehints": "Goose 提示",
    ".aiderrules": "Aider 規則",
    "llms.txt": "給模型讀的站點說明（llms.txt）",
}

# 檔名結尾 → 標籤（Copilot 的分檔格式）
SUFFIX_RULES = (
    (".instructions.md", "GitHub Copilot 指令檔"),
    (".prompt.md", "GitHub Copilot 提示檔"),
)

# 客戶端設定目錄：底下的說明文字同樣會被載入（子代理、斜線指令、規則）
AGENT_DIR_RE = re.compile(
    r"/\.(claude|cursor|windsurf|codex|gemini|clinerules|roo|kilocode)/", re.I)
AGENT_DIR_EXT = (".md", ".mdc", ".txt")

# 沒有副檔名、或副檔名罕見，但仍必須抓下來的指令檔
EXTRA_TEXT_NAMES = frozenset(
    n for n in AGENT_FILE_NAMES if n.startswith(".") or "." not in n)


def kind(path: str) -> str:
    """這個路徑是代理指令檔嗎？是的話回傳它的中文類型，否則回空字串。"""
    p = path.replace("\\", "/").strip("/")
    if not p:
        return ""
    name = p.rsplit("/", 1)[-1].lower()

    if name in AGENT_FILE_NAMES:
        return AGENT_FILE_NAMES[name]
    for suffix, label in SUFFIX_RULES:
        if name.endswith(suffix):
            return label

    low = "/" + p.lower()
    if name.endswith(AGENT_DIR_EXT) and AGENT_DIR_RE.search(low):
        return "AI 客戶端設定目錄下的指令檔"
    if name.endswith(".mdc") and "/rules/" in low:
        return "Cursor 規則檔（.mdc）"
    return ""
