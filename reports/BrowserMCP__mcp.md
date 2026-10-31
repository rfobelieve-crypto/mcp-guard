# MCP 安檢報告：BrowserMCP/mcp

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `BrowserMCP/mcp` |
| 專案說明 | Browser MCP is a Model Context Provider (MCP) server that allows AI applications |
| 星數 / Fork | ⭐ 7254 / 598 |
| 最後更新 | 2026-10-30 |
| 授權 | Apache License 2.0 |
| npm 套件 | `browsermcp`（registry 查無） |
| 已掃描檔案 | 134 個 |
| 檢查時間 | 2026-10-31 00:24 |

## 風險摘要

🟠 高 1　🟡 中 2　🔵 低 5　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「瀏覽器／網頁自動化」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`packages/mcp/eval/run.eval.ts`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 13 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`a.example、addons.opera.com、browsermcp.io、chrome.google.com、chromewebstore.google.com、json.schemastore.org、microsoftedge.microsoft.com、nodejs.org、pay.example、shop.example…`

### 🔵 低｜[供應鏈] 有 2 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`oxfmt@^0.72.0、oxlint@^1.87.0`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`apps/extension/scripts/smoke-browser-control.ts、packages/mcp/spikes/hidden-tabs/covered-probe.ts、packages/mcp/spikes/hidden-tabs/focus-steal.ts、packages/mcp/spikes/hidden-tabs/lib.ts、packages/mcp/spikes/hidden-tabs/probe.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`apps/extension/scripts/smoke-browser-control.ts、packages/extension-core/src/background/browser-control.test.ts、packages/extension-core/src/background/connection.test.ts、packages/extension-core/src/background/connection.ts、packages/extension-core/src/background/fake-daemon.test-helper.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`apps/extension/scripts/smoke-browser-control.ts、packages/mcp/eval/run.eval.ts、packages/mcp/spikes/hidden-tabs/hidden-tabs.test.ts、packages/mcp/spikes/hidden-tabs/lib.ts、packages/mcp/src/commands/targets.test.ts`

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 已掃描 2 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、packages/mcp/AGENTS.md（Agent 指令（AGENTS.md 慣例））`

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（browsermcp）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 25 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：瀏覽器／網頁自動化

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 1 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-10-30`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 7254｜fork 598｜語言 TypeScript｜建立 2025-03-28｜最後推送 2026-10-30

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*