# MCP 安檢報告：modelcontextprotocol/inspector

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `modelcontextprotocol/inspector` |
| 專案說明 | Visual testing tool for MCP servers |
| 星數 / Fork | ⭐ 10495 / 1442 |
| 最後更新 | 2026-07-28 |
| 授權 | Other |
| npm 套件 | `@modelcontextprotocol/inspector` |
| 已掃描檔案 | 173 個 |
| 檢查時間 | 2026-07-28 01:11 |

## 風險摘要

🟡 中 2　🔵 低 5　⚪ 資訊 5

## 詳細發現

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "husky && npm run build"`

### 🟡 中｜[權限] 會連往 16 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`custom-auth.example.com、datatracker.ietf.org、eslint.org、feross.org、oauth.example.com、opencollective.com、paulmillr.com、paypal.me、playwright.dev、polar.sh…`

### 🔵 低｜[供應鏈] 有 21 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@modelcontextprotocol/inspector-cli@^1.0.0、@modelcontextprotocol/inspector-client@^1.0.0、@modelcontextprotocol/inspector-server@^1.0.0、@modelcontextprotocol/sdk@^1.25.2、concurrently@^9.2.0、node-fetch@^3.3.2…`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`cli/__tests__/helpers/cli-runner.ts、cli/scripts/make-executable.js、client/src/__tests__/proxyFetchEndpoint.test.ts、scripts/update-version.js`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`cli/__tests__/helpers/cli-runner.ts、cli/__tests__/helpers/test-fixtures.ts、cli/__tests__/helpers/test-server-stdio.ts、cli/src/cli.ts、cli/src/transport.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`cli/__tests__/helpers/fixtures.ts、cli/src/cli.ts、client/bin/client.js、client/bin/start.js、client/src/components/AppRenderer.tsx`

### 🔵 低｜[維護] 未處理 issue 偏多（312 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 31 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：瀏覽器／網頁自動化

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-28`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 10495｜fork 1442｜語言 TypeScript｜建立 2024-10-03｜最後推送 2026-07-28

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*