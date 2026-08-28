# MCP 安檢報告：idosal/git-mcp

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `idosal/git-mcp` |
| 專案說明 | Put an end to code hallucinations! GitMCP is a free, open-source, remote MCP ser |
| 星數 / Fork | ⭐ 8355 / 741 |
| 最後更新 | 2026-05-08 |
| 授權 | Apache License 2.0 |
| npm 套件 | `git-mcp` |
| 已掃描檔案 | 120 個 |
| 檢查時間 | 2026-08-28 05:07 |

## 風險摘要

🟡 中 2　🔵 低 7　⚪ 資訊 5

## 詳細發現

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "husky"`

### 🟡 中｜[權限] 會連往 49 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`augmentcode.com、autorag-cache.gitmcp.internal、biomejs.dev、cdn.prod.website-files.com、cdn.tailwindcss.com、chat-api-worker.idosalomon.workers.dev、claude.ai、cline.bot、cline.tools、code.visualstudio.com…`

### 🔵 低｜[供應鏈] 有 66 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@ai-sdk/anthropic@^1.2.10、@ai-sdk/cohere@^1.2.9、@ai-sdk/google@^1.2.13、@ai-sdk/groq@^1.2.8、@ai-sdk/openai@^1.3.20、@ai-sdk/react@^1.2.9…`

### 🔵 低｜[供應鏈] npm 套件未標示原始碼位置

套件沒有填 repository 欄位，因此**無法自動核對**它是否真的由這個 repo 建置。這不代表有問題，但也代表少了一道可驗證性；安裝前建議自行確認發布者身分。

> 證據：`npm: git-mcp（repository 欄位空白）`

### 🔵 低｜[工具描述投毒] 描述含「優先呼叫本工具」的措辭

這在正常 MCP 中很常見（引導模型選對工具），但也是投毒用來搶奪呼叫權的手法。請確認它引導的方向合理、且沒有附帶額外指令。

> 證據：`src/api/tools/commonTools.ts｜「Fetch entire documentation file from the ${owner}/${repo} GitHub Pages. Useful for general questions. Always call this t」`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`app/chat/components/chat-sidebar.tsx、app/components/content.tsx、app/routes/_index.tsx、worker-configuration.d.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`dist/tools/index.js、playwright.config.ts`

### 🔵 低｜[維護] 未處理 issue 偏多（78 則）

可能代表維護者回應不及，遇到問題時求助無門。

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 112 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-05-08`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 8355｜fork 741｜語言 TypeScript｜建立 2025-03-29｜最後推送 2026-05-08

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*