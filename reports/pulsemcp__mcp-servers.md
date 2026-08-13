# MCP 安檢報告：pulsemcp/mcp-servers

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `pulsemcp/mcp-servers` |
| 專案說明 | MCP (Model Context Protocol) Servers authored and maintained by the PulseMCP tea |
| 星數 / Fork | ⭐ 76 / 9 |
| 最後更新 | 2026-07-26 |
| 授權 | MIT License |
| npm 套件 | `mcp-servers-monorepo`（registry 查無） |
| 已掃描檔案 | 476 個 |
| 檢查時間 | 2026-08-12 21:48 |

## 風險摘要

🟠 高 1　🟡 中 4　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「開發框架／工具鏈」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`experimental/fetchpet/shared/src/server.ts`

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "husky install"`

### 🟡 中｜[工具描述投毒] 描述中出現系統提示詞標記或字樣

描述裡出現 <system> 之類的標記，可能是想偽裝成系統訊息。請確認上下文。

> 證據：`experimental/claude-code-agent/shared/src/tools/init-agent.ts｜「Initializes a Claude Code subagent with a custom system prompt and working directory. This tool creates a new Claude Cod」`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 20 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`accounts.google.com、appsignal.com、console.cloud.google.com、docs.appsignal.com、dotenvx.com、fly.io、gmail.googleapis.com、mail.google.com、my.fetchpet.com、myaccount.google.com…`

### 🔵 低｜[供應鏈] 有 8 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@types/jsdom@^21.1.7、@typescript-eslint/eslint-plugin@^8.19.0、@typescript-eslint/parser@^8.19.0、eslint@^8.57.0、eslint-config-prettier@^9.1.0、husky@^8.0.3…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/scripts/mcp-registry-scan.mjs、.github/workflows/publish-mcp-servers.yml、experimental/claude-code-agent/shared/src/claude-code-client/claude-code-client.ts、experimental/claude-code-agent/shared/src/resources.ts、experimental/claude-code-agent/shared/src/tools/get-server-capabilities.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/publish-mcp-servers.yml、experimental/agent-orchestrator/local/src/index.integration-with-mock.ts、experimental/agent-orchestrator/local/src/index.ts、experimental/agent-orchestrator/shared/src/allowed-agent-roots.ts、experimental/agent-orchestrator/shared/src/logging.ts`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`experimental/agent-orchestrator/local/prepare-publish.js、experimental/appsignal/local/prepare-publish.js、experimental/claude-code-agent/local/prepare-publish.js、experimental/claude-code-agent/shared/src/claude-code-client/claude-code-client.ts、experimental/claude-code-agent/shared/src/server-installer/claude-client-adapter.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 4 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、experimental/AGENTS.md（Agent 指令（AGENTS.md 慣例））、libs/mcp-server-template/AGENTS.md（Agent 指令（AGENTS.md 慣例））、libs/mcp-server-template/shared/src/example-client/AGENTS.md（Agent 指令（AGENTS.md 慣例））`

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（mcp-servers-monorepo）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 17 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-26`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 com.pulsemcp/google-calendar`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 76｜fork 9｜語言 TypeScript｜建立 2025-05-12｜最後推送 2026-07-26

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*