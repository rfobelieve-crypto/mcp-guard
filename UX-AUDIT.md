# UX-AUDIT.md — Phase 0 現況稽核

> 依 `UX-TASK-BRIEF.md` Phase 0 產出。只讀程式碼與跑 Lighthouse，未改動任何檔案。
> 完成後停下，待 Austin 確認再進 Phase 1。

---

## 方法說明

網站是純靜態輸出：`site.py`(單一 1,323 行 Python 檔)讀 `reports/data.json`，
把四頁 HTML 直接產生到 `site/`，`vercel.json` 設定 `framework: null`、無
build command，Vercel 只是把 `site/` 原封不動發布。因此本機跑
`python3 -m http.server` 服務 `site/` 目錄，效果與線上版本逐位元組相同。

由於這個 session 的網路政策擋掉了 `mcp-guard-iota.vercel.app`(見前一輪的
403 記錄)，Lighthouse 是對**本機靜態伺服**跑的，而不是直接打線上網址——
但因為兩者是同一份檔案，結果應可視為線上版本的可靠基準。

環境：Chromium 13.4.1(Playwright 內建)、Lighthouse 13.4.1、
`--form-factor=mobile --throttling-method=simulate`。

---

## 1. `/registry` 稽核卡片預設收合還是展開?

**預設收合。** 每筆是原生 `<details class="row">`，`render_rows()`
(site.py:747-793)產生的 HTML 完全沒有 `open` 屬性，也沒有任何 JS 在載入時
呼叫展開——收合/展開純粹交給瀏覽器原生行為，使用者要點 `<summary>` 才會看到
完整發現清單。

`<summary>` 本身已經做了輕量分層：結論徽章、slug、發布者身分標籤、
最高風險一句話摘要(`top`，超標項目會加粗)、簡介、星數/更新時間，都在收合狀態
就看得到。**跟 Phase 1 要求相比，這部分「摘要在收合狀態可見」其實已經做了**，
缺的是「查看 N 項發現 →」這種明確計數，以及展開狀態的 URL 保存(deep link)。

## 2. 搜尋框?篩選器是即時互動還是重整頁面?

**都是即時互動，無頁面重整。** `/registry` 有：
- 一個 `<input type="search" id="q">`(site.py:1014)
- 4 個結論篩選 chip：全部/不要安裝/需複核/已通過
- 用途分類 chip(`cat_chips()`)

`FILTER_JS`(site.py:664-717)全部在客戶端完成：每個 `<details>` 上有
`data-v`(結論)、`data-c`(能力)、`data-d`(領域)、`data-search`(拼接 slug/
簡介/摘要/發布者/用途分類/topics 的小寫字串)，篩選只是切換 `hidden` 屬性、
更新命中計數，沒有任何網路請求或重整。三個維度(結論/能力/領域)可疊加。

`/pick` 頁的「看這類全部 N 個 →」連結會帶 `?c=xxx` 或 `?d=xxx` query
string，`/registry` 載入時讀取這個參數並自動觸發對應 chip(site.py:696-715)。

**目前沒有的**:個別 `<details>` 展開狀態不會寫進網址(無 `pushState`/
`location.hash`)——分享單一結果連結目前做不到，需要在 Phase 1 補上。

## 3. 178 筆資料是一次載入、分頁,還是無限捲動?

**一次全部載入，全部在建置期就烤進 HTML，沒有分頁、沒有無限捲動、
也沒有任何 client-side 的 JSON fetch。**

- `reports/data.json` 857 KB，只被 Python 產生器讀取(site.py:40)，
  **從未被送到瀏覽器**——site.py 全檔沒有 `fetch(`/`XMLHttpRequest`/
  對 data.json 的任何客戶端引用。
- `page_registry()` 呼叫 `render_rows(projects)` 把全部 178 筆字串拼接
  進同一份 HTML，寫死在 `site/registry/index.html`。
- **該檔案原始大小 1,039,982 bytes(≈1.04 MB)**，gzip 後 ≈101.6 KB
  (`gzip -c site/registry/index.html | wc -c` = 103,604)。

這是目前最大的效能瓶頸，見下方 Lighthouse 結果。

## 4. `/pick`(該裝哪個)頁面的實際互動流程

`page_pick()`(site.py:1029-1099)依兩個維度分組，各自呈現：

1. **按你要做的事**(`DOMAIN_SCENES`，8 類：finance/data/web/media/
   productivity/health/research/infra)
2. **按你要的能力**(`SCENES`，9 類：browser/code/database/cloud/desktop/
   api/docs/filesystem/devtool)

每組先依結論排序(🟢 通過 > 🟡 複核 > 🔴 不要安裝)、同結論再依星數排序，
只列出前 5 筆。每一列**直接連到 GitHub 原始 repo**(`target="_blank"`)，
**不是**連到 `/registry` 裡對應的那一筆稽核詳情——想看完整發現清單得自己
去 `/registry` 用搜尋框找。超過 5 筆的分類，才有「看這類全部 N 個 →」連到
`/registry/?d=xxx`(帶著篩選參數，見上題)。沒有資料的分類整段不輸出
(`wrap_sec` 的空內容檢查)。

**缺口**:從 `/pick` 點進 GitHub 之後，使用者若想回頭看該專案完整的稽核
證據，目前得手動切到 `/registry` 再搜尋一次——沒有直接跳轉到該筆展開狀態
的路徑，這跟第 2 題提到的 deep-link 缺口是同一個根因。

## 5. CLI 能否查詢未收錄在 178 筆內的 repo?

**可以，且完全獨立於這 178 筆。** `mcp_guard/cli.py:34` 呼叫
`collect(args.target)`(`mcp_guard/fetch.py`)在執行當下即時向 GitHub／npm
抓原始碼分析，跟 `reports/data.json`、178 筆registry 完全無關。`target`
接受 `owner/repo`、GitHub 網址、或 `npm:套件名`——registry 上的 178 筆只是
「預先跑過、每日 05:00 重驗」的熱門清單，CLI 本身沒有這個限制。

這代表 Phase 4(空查詢引導)技術上是可行的:網站找不到的 repo，CLI 當下
就能查——只是網站本身沒有暴露這條路徑(見下方架構備註，網站是純靜態，
沒有後端可以代跑 CLI)。

## 6. 技術棧、元件架構、樣式方案

- **零前端框架、零建置步驟。** 沒有 `package.json`、沒有 React/Vue/JSX/
  TSX。整個網站由一支 Python 腳本(`site.py`)用 f-string 直接拼接輸出
  4 份完整 HTML 文件到 `site/`。
- **樣式**:單一內嵌 CSS 字串(`CSS = """..."""`，site.py:47-369)，
  用 CSS 自訂屬性做 design token(`--bg`/`--ink`/`--seal`/`--crit`/
  `--warn`/`--pass` 等)，支援 `:root[data-theme="light"]` 覆寫深色預設。
  無 CSS-in-JS、無預處理器、無 CSS framework(non-Tailwind)。
- **JS**:三段內嵌 vanilla script，各自獨立、無共用執行環境：
  - `REVEAL_JS`——`IntersectionObserver` 做捲動漸顯，尊重
    `prefers-reduced-motion`
  - `FILTER_JS`——`/registry` 專用的搜尋/篩選(見第 2 題)
  - `SCENE_JS`——僅首頁，手寫透視投影(非 WebGL/Three.js)的 3D 球體動畫，
    ~50 行三維數學
- **部署**:`vercel.json` 設 `framework: null`、`outputDirectory: "site"`、
  無 build/install command，代表 Vercel 只是直接發布 `site/` 資料夾原封
  不動的靜態檔案；同一份輸出也部署在 GitHub Pages 當備援(`SITE_URL`
  常數處理 canonical，避免重複內容)。
- **無元件架構**(SPA 意義上的)：四頁由 `page()`(site.py:887)套共用
  骨架(`nav()` + body + `foot()`)，本質是伺服器端字串模板，不是可獨立
  reuse/state 的元件系統。這對 Phase 1「分層揭露的狀態管理」有直接影響——
  目前沒有任何前端狀態框架可用，任何互動狀態都得用最原始的 vanilla JS
  + `data-*` 屬性(如同 FILTER_JS 現在的做法)手刻。

## 7. 行動裝置斷點設計現況

CSS 內共 3 個 `@media` 斷點(皆為 `max-width`，無 `min-width`)：

| 斷點 | 影響範圍 |
|---|---|
| `720px` | `.nav`：導覽列換行、menu 換到第三順位、間距縮小 |
| `840px` | `.split`：兩欄區塊(方法頁等)收成單欄 |
| `620px` | `.row summary` 改成兩欄 grid(星數/時間換到第二列)、頁尾 `.facts` 間距縮小、`section.blk` 內距縮小 |

`.controls`(搜尋框 + 篩選 chip 那排)**沒有專屬斷點**，靠
`display:flex;flex-wrap:wrap` 自然換行——實測(見下方 Lighthouse 截圖等
效資料)在手機寬度下可正常換行不溢出，但沒有針對小螢幕特別調整過 chip
大小或觸控熱區，屬於「堪用但非刻意設計」。

無障礙現況：嚴重度標籤(`sev CRITICAL/HIGH/MEDIUM/LOW`)已經是「顏色 +
文字」雙重編碼(non-color-only)，符合任務書全案約束第 4 條的要求，
**這部分已經做到，不需要在 Phase 2 額外補**。

---

## Lighthouse 基準(行動裝置模式，模擬節流)

| 頁面 | Performance | LCP | TBT | Speed Index | FCP | TTI |
|---|---|---|---|---|---|---|
| `/`(首頁) | **97** | 1.4 s | 130 ms | 3.9 s | 1.2 s | 1.5 s |
| `/registry/` | **54** | 6.3 s | 360 ms | 6.1 s | 6.1 s | 6.7 s |
| `/pick/` | **100** | 1.4 s | 0 ms | 1.1 s | 1.1 s | 1.4 s |

CLS 三頁皆為 0。

**`/registry/` 是全案效能瓶頸**，與第 3 題的結構性原因直接對應：
1.04 MB 的單一 HTML(178 筆全展開的 DOM，即使收合也要整包下載並解析)
把 LCP/FCP 拖到 6 秒以上。Phase 1 的分層揭露如果能同時減少初始 DOM
節點數(而不只是視覺上收合)，應該能大幅改善這裡的分數——這點在
Phase 1 動工時建議一併納入驗收標準，不只是「卡片高度不超過三行」。

---

## 給 Phase 1 的補充觀察(不影響現有驗收標準，僅供參考)

- 收合狀態的資訊分層其實已經有一部分基礎(摘要在 `<summary>` 內)，
  Phase 1 主要缺口是：①「查看 N 項發現 →」的明確計數 UI ②展開狀態
  deep link ③把「省 DOM 節點」也當成效能目標，不是只做視覺收合。
- 沒有任何前端框架/狀態管理可依賴，deep link 與分層揭露的狀態都得用
  vanilla JS + URL(`history.pushState` 或 `location.hash`)手刻，
  這呼應任務書「模型分工」中列的升級觸發點 #2(狀態管理方案選擇)——
  這裡確實是需要決策的點，因為目前的架構完全沒有前例可循。
- Phase 4(空查詢引導)在後端能力上可行(CLI 可查任意 repo)，但網站是
  純靜態、無後端，「提交稽核請求」入口目前沒有地方可以送出/儲存這個
  請求(沒有 API route、沒有資料庫)——這需要在 Phase 4 動工前先跟
  Austin 確認要不要新增最小後端(例如 Vercel serverless function + 某種
  儲存)，這已經超出「純前端 UI/UX」的邊界，屬於任務書第 0 節提到的
  「共同開發者專案，先停下來說明」的情況。
