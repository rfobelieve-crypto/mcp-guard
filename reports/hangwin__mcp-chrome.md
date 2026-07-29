# MCP 安檢報告：hangwin/mcp-chrome

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `hangwin/mcp-chrome` |
| 專案說明 | Chrome MCP Server is a Chrome extension-based Model Context Protocol (MCP) serve |
| 星數 / Fork | ⭐ 12227 / 1113 |
| 最後更新 | 2026-01-06 |
| 授權 | MIT License |
| npm 套件 | `mcp-chrome-bridge-monorepo`（registry 查無） |
| 已掃描檔案 | 405 個 |
| 檢查時間 | 2026-07-29 22:00 |

## 風險摘要

🟠 高 1　🟡 中 4　🔵 低 4　⚪ 資訊 6

## 詳細發現

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「瀏覽器／網頁自動化」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`app/chrome-extension/entrypoints/background/record-replay/actions/handlers/extract.ts、app/chrome-extension/entrypoints/background/record-replay/actions/handlers/script.ts、app/chrome-extension/entrypoints/background/record-replay/nodes/conditional.ts、app/chrome-extension/entrypoints/background/tools/browser/inject-script.ts、app/chrome-extension/entrypoints/background/tools/browser/userscript.ts`

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "husky"`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 23 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`ads.example.com、any.com、before.example、chrome.google.com、code.google.com、developer.chrome.com、developer.mozilla.org、docs.example.com、en.wikipedia.org、example.com.evil.com…`

### 🟡 中｜[維護] 約 7 個月沒有更新

更新頻率偏低，導入前先確認它仍相容你的 MCP 客戶端。

> 證據：`最後推送 2026-01-06`

### 🔵 低｜[供應鏈] 有 15 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@commitlint/cli@^19.8.1、@commitlint/config-conventional@^19.8.1、@eslint/js@^9.25.1、@typescript-eslint/eslint-plugin@^8.32.0、@typescript-eslint/parser@^8.32.0、eslint@^9.26.0…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`app/chrome-extension/entrypoints/background/record-replay-v3/storage/db.ts、app/chrome-extension/entrypoints/background/utils/sidepanel.ts`

### 🔵 低｜[維護] 未處理 issue 偏多（225 則）

可能代表維護者回應不及，遇到問題時求助無門。

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（mcp-chrome-bridge-monorepo）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 17 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：瀏覽器／網頁自動化

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 12227｜fork 1113｜語言 TypeScript｜建立 2025-06-09｜最後推送 2026-01-06

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*