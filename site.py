# -*- coding: utf-8 -*-
"""網站產生器：reports/data.json → 單一自足 HTML。

設計立場：這是**儀表板**不是文章——要能一眼看出「哪個需要注意」。
因此摘要在最上、每列左側用嚴重度色條、判定做成檢驗印記；
語意色（紅／琥珀／綠）與主色（檢驗藍）分離，避免「有顏色」等於「有問題」。

用法：
    python site.py                # 產生 site/index.html（可直接部署）
    python site.py --fragment     # 產生 site/fragment.html（給 Artifact 用）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "reports" / "data.json"
OUTDIR = ROOT / "site"

CSS = """
:root{
  --paper:#F4F6F9; --surface:#FFFFFF; --surface-2:#EDF1F6;
  --ink:#131824; --muted:#5A6478; --line:#DCE2EB;
  --seal:#2C4A72;                        /* 主色：檢驗藍 */
  --crit:#B3261E; --warn:#8A6100; --pass:#1B6B4A;   /* 語意色，與主色分離 */
  --crit-bg:#FBEAE8; --warn-bg:#FAF2DF; --pass-bg:#E6F2EC;
  --mono:ui-monospace,"Cascadia Mono",Consolas,"SF Mono",Menlo,monospace;
  --sans:system-ui,-apple-system,"Noto Sans TC","PingFang TC",
        "Microsoft JhengHei","Heiti TC",sans-serif;
  --r:6px;
}
@media (prefers-color-scheme:dark){
  :root{
    --paper:#0E1219; --surface:#151A24; --surface-2:#1B222E;
    --ink:#E3E8F1; --muted:#8B95A9; --line:#252D3B;
    --seal:#7CA3D8;
    --crit:#F08079; --warn:#D9A93C; --pass:#5EC194;
    --crit-bg:#2A1614; --warn-bg:#261E0E; --pass-bg:#112319;
  }
}
:root[data-theme="dark"]{
  --paper:#0E1219; --surface:#151A24; --surface-2:#1B222E;
  --ink:#E3E8F1; --muted:#8B95A9; --line:#252D3B;
  --seal:#7CA3D8;
  --crit:#F08079; --warn:#D9A93C; --pass:#5EC194;
  --crit-bg:#2A1614; --warn-bg:#261E0E; --pass-bg:#112319;
}
:root[data-theme="light"]{
  --paper:#F4F6F9; --surface:#FFFFFF; --surface-2:#EDF1F6;
  --ink:#131824; --muted:#5A6478; --line:#DCE2EB;
  --seal:#2C4A72;
  --crit:#B3261E; --warn:#8A6100; --pass:#1B6B4A;
  --crit-bg:#FBEAE8; --warn-bg:#FAF2DF; --pass-bg:#E6F2EC;
}

*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
     line-height:1.6;-webkit-font-smoothing:antialiased}
.wrap{max-width:1080px;margin:0 auto;padding:40px 20px 72px}

/* ── 頁首 ───────────────────────────────────────────── */
header{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:28px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.18em;
         color:var(--seal);text-transform:uppercase;margin:0 0 10px}
h1{margin:0;font-size:clamp(26px,4.2vw,38px);font-weight:800;
   letter-spacing:-.02em;text-wrap:balance}
.tagline{margin:10px 0 0;color:var(--muted);max-width:62ch;font-size:15px}
.meta{margin-top:14px;font-family:var(--mono);font-size:12px;color:var(--muted)}

/* ── 摘要帶：最重要的「一眼看懂」 ─────────────────────── */
.summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
         gap:12px;margin-bottom:26px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);
      padding:16px 18px;border-left:4px solid var(--tone,var(--muted))}
.stat .n{font-family:var(--mono);font-size:34px;font-weight:700;line-height:1;
         color:var(--tone,var(--ink));font-variant-numeric:tabular-nums}
.stat .k{margin-top:7px;font-size:13px;color:var(--muted)}
.stat.pass{--tone:var(--pass)} .stat.warn{--tone:var(--warn)}
.stat.crit{--tone:var(--crit)} .stat.total{--tone:var(--seal)}

/* ── 控制列 ─────────────────────────────────────────── */
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:16px}
.chip{font:inherit;font-size:13px;padding:7px 14px;border-radius:100px;cursor:pointer;
      background:var(--surface);color:var(--muted);
      border:1px solid var(--line);transition:.15s}
.chip:hover{border-color:var(--seal);color:var(--ink)}
.chip[aria-pressed="true"]{background:var(--ink);color:var(--paper);
                           border-color:var(--ink)}
input[type=search]{flex:1;min-width:180px;font:inherit;font-size:14px;
  padding:8px 13px;border-radius:var(--r);border:1px solid var(--line);
  background:var(--surface);color:var(--ink)}
input[type=search]:focus-visible,.chip:focus-visible,summary:focus-visible{
  outline:2px solid var(--seal);outline-offset:2px}

/* ── 稽核列 ─────────────────────────────────────────── */
.rows{display:flex;flex-direction:column;gap:8px}
details.row{background:var(--surface);border:1px solid var(--line);
  border-left:4px solid var(--tone);border-radius:var(--r);overflow:hidden}
details.row[data-v="crit"]{--tone:var(--crit)}
details.row[data-v="warn"]{--tone:var(--warn)}
details.row[data-v="pass"]{--tone:var(--pass)}
details.row[hidden]{display:none}
summary{list-style:none;cursor:pointer;padding:13px 16px;display:grid;
  grid-template-columns:auto 1fr auto;gap:12px;align-items:center}
summary::-webkit-details-marker{display:none}
summary:hover{background:var(--surface-2)}
.seal{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;font-weight:700;
  padding:5px 9px;border:1px solid currentColor;border-radius:3px;white-space:nowrap}
.seal.crit{color:var(--crit);background:var(--crit-bg)}
.seal.warn{color:var(--warn);background:var(--warn-bg)}
.seal.pass{color:var(--pass);background:var(--pass-bg)}
.name{font-family:var(--mono);font-size:14px;font-weight:600;word-break:break-all}
.top{font-size:12.5px;color:var(--muted);margin-top:3px}
.top b{color:var(--crit);font-weight:600}
.nums{font-family:var(--mono);font-size:12px;color:var(--muted);text-align:right;
  white-space:nowrap;font-variant-numeric:tabular-nums}

/* ── 展開內容 ───────────────────────────────────────── */
.body{padding:4px 16px 18px;border-top:1px solid var(--line)}
.desc{font-size:13px;color:var(--muted);margin:12px 0 14px}
.f{padding:11px 0;border-top:1px dashed var(--line)}
.f:first-of-type{border-top:none}
.fh{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.sev{font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.08em;
  padding:2px 6px;border-radius:3px;white-space:nowrap}
.sev.CRITICAL{color:var(--crit);background:var(--crit-bg)}
.sev.HIGH{color:var(--warn);background:var(--warn-bg)}
.sev.MEDIUM{color:var(--muted);background:var(--surface-2)}
.sev.LOW,.sev.INFO{color:var(--muted);background:transparent;
  border:1px solid var(--line)}
.ft{font-size:14px;font-weight:600}
.fc{font-family:var(--mono);font-size:11px;color:var(--muted)}
.fd{font-size:13.5px;color:var(--muted);margin:5px 0 0;max-width:70ch}
.ev{margin-top:7px;font-family:var(--mono);font-size:11.5px;color:var(--muted);
  background:var(--surface-2);padding:7px 10px;border-radius:4px;
  overflow-x:auto;white-space:pre-wrap;word-break:break-all}
.links{margin-top:14px;font-size:13px}
.links a{color:var(--seal);text-decoration:none;border-bottom:1px solid transparent}
.links a:hover{border-bottom-color:var(--seal)}

/* ── 頁尾 ───────────────────────────────────────────── */
footer{margin-top:40px;padding-top:22px;border-top:1px solid var(--line);
  font-size:13px;color:var(--muted);max-width:72ch}
footer h2{font-size:14px;color:var(--ink);margin:0 0 10px;letter-spacing:.01em}
footer li{margin-bottom:6px}
.empty{padding:36px;text-align:center;color:var(--muted);font-size:14px}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
@media (max-width:620px){
  summary{grid-template-columns:auto 1fr}
  .nums{grid-column:2;text-align:left}
}
"""

JS = """
(function(){
  var rows=[].slice.call(document.querySelectorAll('details.row'));
  var chips=[].slice.call(document.querySelectorAll('.chip'));
  var q=document.getElementById('q');
  var empty=document.getElementById('empty');
  var filter='all';
  function apply(){
    var t=(q.value||'').toLowerCase().trim();
    var shown=0;
    rows.forEach(function(r){
      var okV = filter==='all' || r.dataset.v===filter;
      var okT = !t || r.dataset.search.indexOf(t)>-1;
      var vis = okV && okT;
      r.hidden = !vis;
      if(vis) shown++;
    });
    empty.hidden = shown>0;
  }
  chips.forEach(function(c){
    c.addEventListener('click',function(){
      chips.forEach(function(o){o.setAttribute('aria-pressed', o===c);});
      filter=c.dataset.f; apply();
    });
  });
  q.addEventListener('input',apply);
})();
"""


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


VKEY = {"🔴": "crit", "🟡": "warn", "🟢": "pass"}


def build(data: dict) -> str:
    projects = data["projects"]
    n = {"crit": 0, "warn": 0, "pass": 0}
    for p in projects:
        n[VKEY.get(p["verdict"][0], "pass")] += 1

    rows = []
    for p in projects:
        v = VKEY.get(p["verdict"][0], "pass")
        label = p["verdict"][2:]
        search = f"{p['slug']} {p.get('desc','')} {p['top']}".lower()

        fs = []
        for f in p["findings"]:
            ev = (f'<div class="ev">{esc(f["evidence"])}</div>'
                  if f.get("evidence") else "")
            fs.append(
                f'<div class="f"><div class="fh">'
                f'<span class="sev {esc(f["severity"])}">{esc(f["severity"])}</span>'
                f'<span class="ft">{esc(f["title"])}</span>'
                f'<span class="fc">{esc(f["check"])}</span></div>'
                f'<p class="fd">{esc(f["detail"])}</p>{ev}</div>')

        top = esc(p["top"])
        if "超出宣稱用途" in p["top"] or p["crit"]:
            top = f"<b>{top}</b>"

        rows.append(
            f'<details class="row" data-v="{v}" data-search="{esc(search)}">'
            f'<summary>'
            f'<span class="seal {v}">{esc(label)}</span>'
            f'<span><span class="name">{esc(p["slug"])}</span>'
            f'<span class="top">{top}</span></span>'
            f'<span class="nums">★{p["stars"]:,}<br>{esc(p["pushed"])}</span>'
            f'</summary>'
            f'<div class="body">'
            f'<p class="desc">{esc(p.get("desc") or "（此專案未填寫說明）")}</p>'
            f'{"".join(fs)}'
            f'<p class="links">'
            f'<a href="https://github.com/{esc(p["slug"])}" '
            f'target="_blank" rel="noopener">GitHub 專案 ↗</a>　'
            f'<span class="fc">已掃描 {p["files"]} 個檔案</span></p>'
            f'</div></details>')

    return f"""<title>MCP 安檢｜獨立稽核總表</title>
<style>{CSS}</style>
<div class="wrap">
<header>
  <p class="eyebrow">獨立稽核 · 繁體中文</p>
  <h1>MCP 安檢總表</h1>
  <p class="tagline">安裝任何 MCP 之前，先看清楚它是誰、要什麼權限、
  有沒有對模型下你看不到的指令。全部結論都附可自行複現的證據。</p>
  <p class="meta">最近驗證 {esc(data['scanned_at'])}　·　{len(projects)} 個專案　·
  耗時 {data.get('elapsed_sec', 0)} 秒</p>
</header>

<section class="summary">
  <div class="stat pass"><div class="n">{n['pass']}</div>
    <div class="k">未發現明顯風險</div></div>
  <div class="stat warn"><div class="n">{n['warn']}</div>
    <div class="k">需人工複核</div></div>
  <div class="stat crit"><div class="n">{n['crit']}</div>
    <div class="k">不要安裝</div></div>
  <div class="stat total"><div class="n">{sum(len(p['findings']) for p in projects)}</div>
    <div class="k">累計檢查發現</div></div>
</section>

<div class="controls">
  <button class="chip" data-f="all" aria-pressed="true">全部</button>
  <button class="chip" data-f="crit" aria-pressed="false">不要安裝</button>
  <button class="chip" data-f="warn" aria-pressed="false">需複核</button>
  <button class="chip" data-f="pass" aria-pressed="false">已通過</button>
  <input type="search" id="q" placeholder="搜尋專案名稱或風險…"
         aria-label="搜尋專案">
</div>

<div class="rows">{"".join(rows)}</div>
<p class="empty" id="empty" hidden>沒有符合條件的專案。</p>

<footer>
  <h2>這份報告不保證什麼</h2>
  <ul>
    <li><b>這是靜態稽核</b>：只讀原始碼與公開中繼資料，<b>不執行</b>目標程式，
        因此看不到只在執行期才出現的行為。</li>
    <li><b>「未發現明顯風險」不等於安全背書</b>，只代表已知樣式沒有命中。</li>
    <li><b>「需人工複核」不是指控</b>——最常見的原因是這個工具本來就需要大權限。
        重點是你<b>知情</b>。</li>
    <li>本工具開發期間曾對 5 個知名專案產生 6 次誤報，全部在發布前攔下並修正，
        誤報樣本已收進回歸測試。<b>若你是維護者且認為結果有誤，請開 issue。</b></li>
  </ul>
  <p><a class="links" href="https://github.com/rfobelieve-crypto/mcp-guard"
     target="_blank" rel="noopener">原始碼與更正政策 ↗</a></p>
</footer>
</div>
<script>{JS}</script>"""


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not DATA.exists():
        print("找不到 reports/data.json，請先執行：python batch.py")
        return 1
    data = json.loads(DATA.read_text(encoding="utf-8"))
    frag = build(data)
    OUTDIR.mkdir(exist_ok=True)

    if "--fragment" in sys.argv:
        # Artifact 版：發佈時會自動包上 <head>/<body>，這裡不能自帶外層標籤
        out = OUTDIR / "fragment.html"
        out.write_text(frag, encoding="utf-8")
    else:
        # 可直接部署版：把 <title> 放進 head，其餘進 body
        title, _, rest = frag.partition("</title>\n")
        out = OUTDIR / "index.html"
        out.write_text(
            '<!doctype html>\n<html lang="zh-Hant">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            '<meta name="description" content="MCP 安檢：繁體中文的 MCP 獨立'
            '安全稽核。安裝前先看清楚它是誰、要什麼權限、有沒有對模型下指令。">\n'
            f'{title}</title>\n</head>\n<body>\n{rest}\n</body>\n</html>\n',
            encoding="utf-8")
    print(f"已產生 {out}（{out.stat().st_size:,} bytes）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
