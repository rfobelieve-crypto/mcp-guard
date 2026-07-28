# -*- coding: utf-8 -*-
"""應用領域推斷：這個 MCP 是拿來做什麼「事情」的？

和 profile.py 的差別是兩個不同的維度，不能互相取代：

    profile（技術能力）  瀏覽器／程式碼／資料庫／桌面控制…
                        → 用來比對「宣稱用途 vs 實際權限」，服務於安全判斷
    domain （應用領域）  金融／健康／網站／資料分析…
                        → 用來回答「我要做 X，該裝什麼」，服務於選擇

同一個交易工具可以同時是「第三方 API 串接」（技術）與「金融與交易」（領域）。
使用者心裡想的是後者：他要做的是交易策略，不是「串接 API」。

推斷同樣只用**公開自述**（description / topics / 名稱），不看實作。
"""
from __future__ import annotations

import re

from .fetch import RepoBundle

# 領域代號 → (中文名, 比對樣式)
# 排前面的優先命中：具體領域放前面，泛用的放後面。
DOMAINS: list[tuple[str, str, str]] = [
    ("finance", "金融與交易",
     r"trading|trade\b|finance|financial|fintech|stock|equit|crypto|"
     r"bitcoin|ethereum|defi|exchange|brokerage|portfolio|backtest|"
     r"quant\w*|market data|ticker|candlestick|arbitrage|payment|invoice|"
     r"accounting|bookkeep|tax\b|銀行|交易|金融|理財"),

    # 2026-07-28 校準：裸 health 會命中「code health scores」「health check」，
    # 把一個程式碼分析工具歸進醫療類。技術語境裡太常見的詞一律換成具體術語。
    ("health", "健康與醫療",
     r"healthcare|health data|medical|medicine|clinical|patient|hospital|"
     r"\bfhir\b|icd-?1[01]|snomed|\bloinc\b|rxnorm|biomed|genomic|"
     r"nutrition|supplement|fitness|workout|醫療|病歷|營養"),

    ("data", "資料分析與圖表",
     r"analytic|data visuali[sz]|\bchart\b|dashboard|"
     r"data ?science|statistic\w*|spreadsheet|business intelligence|"
     r"報表|圖表|資料分析"),

    ("web", "網站與前端",
     r"website|web ?app|frontend|front-end|landing page|\bcms\b|"
     r"static site|web ?design|tailwind|next\.?js|svelte|"
     r"webflow|wordpress|shopify|網站|前端"),

    # 裸 design 會命中「design system」「designed for」；裸 render 會命中
    # 「rendering engine」。改用實際的媒體處理術語。
    ("media", "影音與設計",
     r"image (generation|editing|processing)|text-to-image|"
     r"\bphoto\b|video (editing|generation)|\baudio\b|speech|voice|music|"
     r"\btts\b|stable diffusion|figma|canva|3d model|blender|"
     r"影音|繪圖|配音"),

    ("productivity", "文書與生產力",
     r"notion|slack|discord|telegram|calendar|gmail|"
     r"todo|task manager|note-?taking|obsidian|\bjira\b|trello|"
     r"\bcrm\b|生產力|筆記|行事曆"),

    ("research", "研究與學術",
     r"arxiv|scholar|pubmed|academic paper|citation|"
     r"research assistant|literature review|學術|論文"),

    # 裸 monitor／logging／deployment 在任何後端專案都會出現。
    ("infra", "基礎設施與維運",
     r"kubernetes|k8s\b|docker|terraform|ansible|observability|"
     r"incident (response|management)|\bsre\b|ci/?cd|serverless|"
     r"prometheus|grafana|維運|部署"),
]

DEFAULT = ("general", "通用工具")


def infer_domain(b: RepoBundle) -> tuple[str, str]:
    """回傳 (領域代號, 中文名)。判不出來就是通用工具。

    **只看 description 與專案名**，不看 topics 也不看 README：
    topics 是專案自己標的行銷標籤（一個資料庫客戶端標了 docker，就會被
    歸進基礎設施），README 則什麼都提到。錯誤分類比未分類更糟——把一個
    程式碼工具放進「健康與醫療」會直接誤導找工具的人，而歸為「通用工具」
    只是少了一層索引。寧可保守。
    """
    blob = f"{b.meta.get('description') or ''} {b.slug}".lower()
    for code, zh, pattern in DOMAINS:
        if re.search(pattern, blob, re.I):
            return code, zh
    return DEFAULT
