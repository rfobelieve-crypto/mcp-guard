# -*- coding: utf-8 -*-
"""產生 OG 分享圖的來源頁（1200×630），供瀏覽器截圖成 PNG。

為什麼不用生成式工具：OG 圖要和網站是同一個世界。用同一份 CSS、同一顆
子集化字體、同一個深空觀測站場景渲染出來的圖，點進去看到的畫面才會和
分享卡片呼應；而且它能帶上真實數字（幾個通過、幾個需複核）——生成的
圖兩件事都做不到。

流程（一次性，產物進版控）：
    python site.py && python make_og.py     # 產生 assets/og/*.html
    # 用瀏覽器逐一開啟並截圖 1200×630 → assets/og/*.png
    python site.py                          # 複製 PNG 到 site/og/

之所以不在 CI 裡自動截圖：那需要在 runner 上裝一整套無頭瀏覽器，
而 OG 圖只有在標題或數字改動時才需要重製。
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 從檔案路徑載入 site.py：`import site` 會拿到 Python 標準庫那個 site
# 模組（直譯器啟動時就已載入），不是這個專案的產生器。
_spec = importlib.util.spec_from_file_location("_sitegen", ROOT / "site.py")
_sitegen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sitegen)
CSS, SCENE_JS, DATA, VKEY, esc = (
    _sitegen.CSS, _sitegen.SCENE_JS, _sitegen.DATA, _sitegen.VKEY, _sitegen.esc)

OUT = ROOT / "assets" / "og"

# 每張圖：檔名、主標（允許 <em> 強調）、腳註
CARDS = [
    ("home", "裝下去之前，<br>先知道它<em>要什麼權限</em>。",
     "獨立稽核 · 繁體中文"),
    ("registry", "{n} 個熱門 MCP，<br><em>逐一查過</em>。", "稽核總表"),
    ("method", "六項檢查，<br><em>全程唯讀</em>。", "怎麼查的"),
    ("trust", "我們<em>預設自己會錯</em>。", "為什麼可信"),
]

# 動畫在截圖情境沒有意義：覆寫 matchMedia 讓場景走「靜態」分支，
# 跑滿 220 幀後停在已經運作一陣子的狀態（有判定過的、有滯留待複核的）。
FREEZE = """
(function(){var m=window.matchMedia.bind(window);
 window.matchMedia=function(q){return /reduce/.test(q)?{matches:true,
   addEventListener:function(){},addListener:function(){}}:m(q);};})();
"""

PAGE = """<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<style>{css}</style>
<style>
html,body{{margin:0;padding:0;width:1200px;height:630px;overflow:hidden}}
.og{{position:relative;width:1200px;height:630px;background:var(--bg);
  display:flex;align-items:center;overflow:hidden}}
.og canvas{{position:absolute;inset:0;width:100%;height:100%}}
.og::after{{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(100deg,var(--bg) 26%,rgba(7,9,14,.55) 52%,
    transparent 76%)}}
.og-in{{position:relative;z-index:2;padding:0 72px;width:100%}}
.og h1{{margin:0;font-family:var(--display);font-size:{size}px;
  font-weight:800;letter-spacing:-.045em;line-height:1.08;
  color:var(--ink);max-width:15ch}}
.og h1 em{{font-style:normal;color:var(--seal)}}
.og .mark{{position:absolute;left:72px;bottom:56px;z-index:2;
  display:flex;align-items:baseline;gap:14px}}
.og .mark b{{font-family:var(--display);font-size:26px;font-weight:700;
  letter-spacing:-.015em;color:var(--ink)}}
.og .mark span{{font-family:var(--mono);font-size:17px;color:var(--muted);
  letter-spacing:.06em}}
.og .stat{{position:absolute;right:72px;bottom:56px;z-index:2;
  font-family:var(--mono);font-size:17px;color:var(--muted);
  letter-spacing:.05em;text-align:right}}
.og .stat b{{color:var(--pass);font-weight:700}}
.og .stat i{{color:var(--warn);font-style:normal;font-weight:700}}
</style></head><body>
<div class="og">
  <canvas id="scene"></canvas>
  <div class="og-in"><h1>{title}</h1></div>
  <div class="mark"><b>MCP 安檢</b><span>{foot}</span></div>
  <div class="stat">{stat}</div>
</div>
<script>{freeze}</script><script>{scene}</script></body></html>
"""


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not DATA.exists():
        print("找不到 reports/data.json，請先執行：python batch.py")
        return 1

    data = json.loads(DATA.read_text(encoding="utf-8"))
    projects = data["projects"]
    n = {"crit": 0, "warn": 0, "pass": 0}
    for p in projects:
        n[VKEY.get(p["verdict"][0], "pass")] += 1

    # 刻意不放「幾個通過／幾個需複核」：那是每天重掃都會變的數字，而 OG 圖
    # 是靜態資產、不會跟著重製。放上去只會讓分享卡片長期顯示過期資訊。
    # 專案總數只在重新同步名單時才變，穩定得多。
    stat = (f'<b>{len(projects)}</b> 個熱門 MCP，逐一查過<br>'
            '每日 05:00 自動重新驗證')

    OUT.mkdir(parents=True, exist_ok=True)
    # 字體以 style.css 為基準寫死成 display.woff2，OG 頁不在同一層，
    # 因此把該行改寫成指得到的相對路徑。
    css = CSS.replace('url("display.woff2")', 'url("../fonts/display.woff2")')

    # 機器人素材同理:OG 頁在 assets/og/ 下,改寫成指得到的路徑。
    scene = SCENE_JS.replace("img.src='robot.webp'",
                             "img.src='../robot/robot.webp'")

    for slug, title, foot in CARDS:
        title = title.format(n=len(projects))
        plain = title.replace("<br>", "").replace("<em>", "").replace("</em>", "")
        html = PAGE.format(css=css, scene=scene, freeze=FREEZE,
                           title=title, foot=esc(foot), stat=stat,
                           size=64 if len(plain) > 14 else 72)
        (OUT / f"{slug}.html").write_text(html, encoding="utf-8")
        print(f"  assets/og/{slug}.html")

    print(f"\n已產生 {len(CARDS)} 張 OG 來源頁。"
          "接著用瀏覽器以 1200×630 逐一截圖，存成同名 .png。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
