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

"""首屏採 premium 處理、總表維持可掃描——兩者共用同一套 token。

刻意不把電影感動態套到稽核表格上：那會傷害掃讀效率，而且對一個
「信任」產品來說，過度炫技反而扣信譽。表格這裡的高級＝精準。
"""

# ── 首屏（深色、獨立於下方主題切換：這是刻意承諾單一視覺世界）──────────
HERO_CSS = """
.hero{position:relative;background:#080B11;color:#E8EDF7;overflow:hidden;
  min-height:min(88vh,720px);display:flex;align-items:center;
  border-bottom:1px solid #1B2331}
.hero canvas{position:absolute;inset:0;width:100%;height:100%;
  display:block;opacity:.9}
.hero-in{position:relative;z-index:1;max-width:1080px;margin:0 auto;
  padding:80px 20px;width:100%}
.hero .eyebrow{color:#6E93C9;margin-bottom:22px}
.hero h1{font-size:clamp(34px,6.4vw,68px);line-height:1.08;font-weight:800;
  letter-spacing:-.035em;margin:0;max-width:16ch;text-wrap:balance;
  color:#F2F5FB}
.hero h1 em{font-style:normal;color:#6E93C9}
.hero p.sub{margin:26px 0 0;font-size:clamp(15px,2vw,19px);line-height:1.65;
  color:#93A0B8;max-width:46ch}
.hero .cta{margin-top:38px;display:flex;gap:12px;flex-wrap:wrap;
  align-items:center}
.hero .cta code{font-family:var(--mono);font-size:14px;background:#111726;
  border:1px solid #222D40;color:#C6D3E8;padding:12px 18px;border-radius:6px}
.hero .cta a{font-size:14px;color:#93A0B8;text-decoration:none;
  border-bottom:1px solid #2A3548;padding-bottom:2px}
.hero .cta a:hover{color:#E8EDF7;border-bottom-color:#6E93C9}
.hero .facts{margin-top:56px;display:flex;gap:34px;flex-wrap:wrap;
  font-family:var(--mono);font-size:12px;color:#63718A;letter-spacing:.04em}
.hero .facts b{display:block;font-size:22px;color:#E8EDF7;font-weight:700;
  margin-bottom:4px;font-variant-numeric:tabular-nums}
@media (prefers-reduced-motion:reduce){.hero canvas{opacity:.45}}
"""

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

# 動畫本身就是產品隱喻：一道掃描光束掃過節點場，多數通過、少數示警。
# 不是裝飾——它在說明這個網站在做什麼。
HERO_JS = """
(function(){
  var c=document.getElementById('field'); if(!c) return;
  var x=c.getContext('2d'), dpr=Math.min(devicePixelRatio||1,2);
  var W,H,nodes=[],sweep=0,still=matchMedia('(prefers-reduced-motion:reduce)').matches;
  var PASS='rgba(94,193,148,', WARN='rgba(217,169,60,', CRIT='rgba(240,128,121,',
      IDLE='rgba(110,147,201,';
  function size(){
    W=c.clientWidth; H=c.clientHeight;
    c.width=W*dpr; c.height=H*dpr; x.setTransform(dpr,0,0,dpr,0,0);
    build();
  }
  function build(){
    nodes=[]; var step=Math.max(52,Math.min(78,W/16));
    for(var gx=step*0.5; gx<W+step; gx+=step)
      for(var gy=step*0.5; gy<H+step; gy+=step){
        var r=Math.random();
        nodes.push({
          x:gx+(Math.random()-0.5)*step*0.55,
          y:gy+(Math.random()-0.5)*step*0.55,
          r:Math.random()*1.3+0.9, lit:0,
          // 比例貼近真實掃描結果：多數通過、少數需複核、極少嚴重
          tone: r>0.965?CRIT : (r>0.80?WARN:PASS)
        });
      }
  }
  function frame(){
    x.clearRect(0,0,W,H);
    var band=170;
    for(var i=0;i<nodes.length;i++){
      var n=nodes[i], d=Math.abs(n.x-sweep);
      if(d<band) n.lit=Math.max(n.lit,1-d/band);
      n.lit*=0.985;
      var a=0.10+n.lit*0.85, col=n.lit>0.16?n.tone:IDLE;
      x.beginPath(); x.fillStyle=col+a.toFixed(3)+')';
      x.arc(n.x,n.y,n.r+n.lit*1.5,0,6.284); x.fill();
      if(n.lit>0.45){
        x.beginPath(); x.strokeStyle=col+(n.lit*0.16).toFixed(3)+')';
        x.lineWidth=1; x.arc(n.x,n.y,4+n.lit*9,0,6.284); x.stroke();
      }
    }
    // 掃描線本身：一道極細的亮邊，不搶戲
    var g=x.createLinearGradient(sweep-120,0,sweep+8,0);
    g.addColorStop(0,'rgba(110,147,201,0)');
    g.addColorStop(1,'rgba(140,178,235,0.18)');
    x.fillStyle=g; x.fillRect(sweep-120,0,128,H);
    x.fillStyle='rgba(168,200,247,0.30)'; x.fillRect(sweep,0,1,H);
  }
  function loop(){ sweep+=1.7; if(sweep>W+200) sweep=-120; frame();
                   requestAnimationFrame(loop); }
  addEventListener('resize',size); size();
  if(still){ sweep=W*0.62; for(var k=0;k<70;k++) frame(); }
  else loop();
})();
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

    total_f = sum(len(p["findings"]) for p in projects)
    return f"""<title>MCP 安檢｜獨立稽核總表</title>
<style>{CSS}{HERO_CSS}</style>

<section class="hero">
  <canvas id="field" aria-hidden="true"></canvas>
  <div class="hero-in">
    <p class="eyebrow">獨立稽核 · 繁體中文</p>
    <h1>裝下去之前，<br>先知道它<em>要什麼權限</em>。</h1>
    <p class="sub">一個 MCP 拿到的不只是你的檔案，是你正在用的那個 AI
    會被誰下指令。我們逐一稽核，每個結論都附你能自己複現的證據。</p>
    <div class="cta">
      <code>mcp-guard owner/repo</code>
      <a href="#registry">看 {len(projects)} 份稽核結果 ↓</a>
    </div>
    <div class="facts">
      <div><b>{n['pass']}</b>未發現明顯風險</div>
      <div><b>{n['warn']}</b>需人工複核</div>
      <div><b>{total_f}</b>累計檢查發現</div>
      <div><b>{esc(data['scanned_at'][:10])}</b>最近驗證</div>
    </div>
  </div>
</section>

<div class="wrap" id="registry">
<header>
  <p class="eyebrow">稽核總表</p>
  <h1>18 個熱門 MCP，逐一查過</h1>
  <p class="tagline">點任一列展開，可看到完整的檢查發現與證據路徑。
  「需人工複核」不是指控——最常見的原因是這個工具本來就需要大權限。</p>
  <p class="meta">最近驗證 {esc(data['scanned_at'])}　·　{len(projects)} 個專案　·
  耗時 {data.get('elapsed_sec', 0)} 秒　·　每日自動重掃</p>
</header>

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
<script>{HERO_JS}</script>
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
