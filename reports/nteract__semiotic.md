# MCP 安檢報告：nteract/semiotic

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `nteract/semiotic` |
| 專案說明 | React data visualization library for streaming, networks, and AI-assisted develo |
| 星數 / Fork | ⭐ 2691 / 136 |
| 最後更新 | 2026-08-21 |
| 授權 | Apache License 2.0 |
| npm 套件 | `semiotic` |
| 已掃描檔案 | 403 個 |
| 檢查時間 | 2026-08-21 21:26 |

## 風險摘要

🟡 中 1　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[權限] 會連往 78 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`americanaejournal.hu、americanarchive.org、api.mapbox.com、api.maptiler.com、api.usaspending.gov、arxiv.org、basemaps.cartocdn.com、bchi.bigcitieshealth.org、blocks.roadtolarissa.com、bost.ocks.org…`

### 🔵 低｜[供應鏈] 有 72 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`d3-array@^3.2.4、d3-brush@^3.0.0、d3-chord@^3.0.1、d3-force@^3.0.0、d3-geo@^3.1.1、d3-hierarchy@^3.1.2…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/publish-mcp-registry.yml、.github/workflows/release.yml、ai/cli.js、ai/mcp-build-info.ts、ai/mcp-http-logging.integration.test.ts`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/release.yml、ai/mcp-http-logging.integration.test.ts、deploy/cloud-run-nightly/verify-runtime.mjs、docs/src/examples/recipes/data/debateWordTrails.build.mjs`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/release.yml、ai/behaviorContracts.cjs、ai/cli.js、ai/mcp-server.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 10 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.agents/skills/blog-post/SKILL.md（Agent Skill 指令（SKILL.md））、.github/copilot-instructions.md（GitHub Copilot 指令）、.github/skills/code-review/SKILL.md（Agent Skill 指令（SKILL.md））、AGENTS.md（Agent 指令（AGENTS.md 慣例））、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、agent-skill/semiotic-charts/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 1522 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-21`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.nteract/semiotic`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 2691｜fork 136｜語言 TypeScript｜建立 2017-03-16｜最後推送 2026-08-21

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*