# MCP 安檢報告：modelcontextprotocol/inspector

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `modelcontextprotocol/inspector` |
| 專案說明 | Visual testing tool for MCP servers |
| 星數 / Fork | ⭐ 10713 / 1488 |
| 最後更新 | 2026-08-20 |
| 授權 | 無 |
| npm 套件 | `@modelcontextprotocol/inspector` |
| 已掃描檔案 | 401 個 |
| 檢查時間 | 2026-08-20 21:26 |

## 風險摘要

🟠 高 1　🟡 中 1　🔵 低 6　⚪ 資訊 6

## 詳細發現

### 🟠 高｜[供應鏈] 安裝時會自動執行腳本：postinstall

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"postinstall": "node scripts/install-clients.mjs"`

### 🟡 中｜[權限] 會連往 26 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`a.example、api.example、api.example.com、as.example、as.example.com、auth.example、auth.example.com、b.example、ctx.example、discord.gg…`

### 🔵 低｜[供應鏈] 有 23 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@hono/node-server@^2.0.12、@modelcontextprotocol/ext-apps@^1.7.4、@napi-rs/keyring@^1.3.0、@vitejs/plugin-react@^6.0.0、ajv@^8.17.1、atomically@^2.1.1…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`clients/cli/__tests__/clear-stored-auth-for-relogin.test.ts、clients/cli/__tests__/helpers/fixtures.ts、clients/cli/src/cli-oauth-navigation.ts、clients/cli/src/open-url.ts、clients/tui/src/utils/openUrl.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`clients/cli/__tests__/clear-stored-auth-for-relogin.test.ts、clients/cli/__tests__/cli-oauth-navigation.test.ts、clients/cli/__tests__/cli.test.ts、clients/cli/__tests__/cliOAuth.test.ts、clients/cli/__tests__/helpers/cli-runner.ts`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`clients/cli/__tests__/e2e.test.ts、clients/launcher/scripts/make-executable.js、clients/web/server/ensure-web-build.ts`

### 🔵 低｜[身分] 沒有授權條款（License）

沒有 LICENSE 檔，法律上你其實沒有被授權使用或散布。

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 已掃描 3 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.github/copilot-instructions.md（GitHub Copilot 指令）、AGENTS.md（Agent 指令（AGENTS.md 慣例））、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 64 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：桌面／終端控制

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-20`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 10713｜fork 1488｜語言 TypeScript｜建立 2024-10-03｜最後推送 2026-08-20

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*