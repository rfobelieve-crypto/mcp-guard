# MCP 安檢報告：nowork-studio/NotFair

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `nowork-studio/NotFair` |
| 專案說明 | Goal-driven, loop-powered marketing agents that crush your business goals 24/7 |
| 星數 / Fork | ⭐ 3311 / 409 |
| 最後更新 | 2026-07-31 |
| 授權 | MIT License |
| 已掃描檔案 | 421 個 |
| 檢查時間 | 2026-08-03 22:11 |

## 風險摘要

🟡 中 1　🔵 低 4　⚪ 資訊 6

## 詳細發現

### 🟡 中｜[權限] 會連往 36 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`MCP.ACME.DEV、access.stripe.com、accounts.google.com、acme.com、acme.test、api.openai.com、auth.acme.dev、broken.example.com、chatgpt.com、developers.facebook.com…`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`notfair/bin/cli.mjs、notfair/bin/native-bindings.mjs、notfair/scripts/copy-standalone-assets.mjs、notfair/src/app/api/chat/route.ts、notfair/src/app/api/restart/route.test.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`notfair/bin/cli.mjs、notfair/src/server/browser/chrome.ts、notfair/src/server/harness-usage.ts、notfair/src/server/mcp-server/tools.test.ts、notfair/src/server/mcp-server/tools.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`notfair/bin/cli.mjs、notfair/src/app/api/agents/[agent]/threads/[thread]/live/route.ts、notfair/src/app/api/restart/route.test.ts、notfair/src/app/api/restart/route.ts、notfair/src/app/api/upgrade/route.test.ts`

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 已掃描 31 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、gemini/SKILL.md（Agent Skill 指令（SKILL.md））、google-ads/audit/SKILL.md（Agent Skill 指令（SKILL.md））、google-ads/copy/SKILL.md（Agent Skill 指令（SKILL.md））、google-ads/landing/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 43 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 4 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-31`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 3311｜fork 409｜語言 TypeScript｜建立 2026-03-27｜最後推送 2026-07-31

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*