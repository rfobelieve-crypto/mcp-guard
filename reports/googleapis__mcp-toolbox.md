# MCP 安檢報告：googleapis/mcp-toolbox

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `googleapis/mcp-toolbox` |
| 專案說明 | MCP Toolbox for Databases is an open source MCP server for databases. |
| 星數 / Fork | ⭐ 16034 / 1655 |
| 最後更新 | 2026-07-28 |
| 授權 | Apache License 2.0 |
| 已掃描檔案 | 400 個 |
| 檢查時間 | 2026-07-28 09:04 |

## 風險摘要

🟡 中 1　🔵 低 4　⚪ 資訊 5

## 詳細發現

### 🟡 中｜[權限] 會連往 23 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.cloudflare.com、bar.com、cloud.google.com、dotenvx.com、feross.org、foo.com、geraintluff.github.io、go.dev、mcp-toolbox.dev、medium.com…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.ci/lint-docs-source-page.sh、.ci/lint-docs-tool-page.sh、.github/workflows/nightly_tier_report.yml、.hugo/static/js/w3.js、cmd/internal/skills/generator.go`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/cloud_build_failure_reporter.yml、.github/workflows/docs_preview_deploy_cf.yaml、cmd/internal/skills/generator.go、cmd/internal/skills/generator_test.go、docs/en/documentation/configuration/pre-post-processing/js/adk/agent.js`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`cmd/internal/skills/generator.go`

### 🔵 低｜[維護] 未處理 issue 偏多（248 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 88 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-28`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 16034｜fork 1655｜語言 Go｜建立 2024-06-07｜最後推送 2026-07-28

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*