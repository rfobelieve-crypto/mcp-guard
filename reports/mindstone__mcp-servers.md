# MCP 安檢報告：mindstone/mcp-servers

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `mindstone/mcp-servers` |
| 專案說明 | Production-ready MCP connectors for popular SaaS tools. Works with Claude Deskto |
| 星數 / Fork | ⭐ 10 / 4 |
| 最後更新 | 2026-08-26 |
| 授權 | Other |
| 已掃描檔案 | 436 個 |
| 檢查時間 | 2026-08-29 03:10 |

## 風險摘要

🟡 中 2　🔵 低 5　⚪ 資訊 6

## 詳細發現

### 🟡 中｜[工具描述投毒] 描述中出現系統提示詞標記或字樣

描述裡出現 <system> 之類的標記，可能是想偽裝成系統訊息。請確認上下文。

> 證據：`connectors/browserbase/src/tools/agent-runs.ts｜「Start an agent run: an AI agent drives a cloud browser to accomplish a natural-language task (extract data, fill forms, 」`

### 🟡 中｜[權限] 會連往 24 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.browserbase.com、api.elevenlabs.io、api.example.com、api.fathom.ai、cdn.browserbase.com、docs.github.com、elevenlabs.io、evil.example、example.org、fathom.video…`

### 🔵 低｜[工具描述投毒] 描述含「優先呼叫本工具」的措辭

這在正常 MCP 中很常見（引導模型選對工具），但也是投毒用來搶奪呼叫權的手法。請確認它引導的方向合理、且沒有附帶額外指令。

> 證據：`connectors/browser-automation/src/tools/observation.ts｜「Get the page accessibility tree with interactive element references.

THIS IS YOUR PRIMARY DISCOVERY TOOL. Always call t」`

### 🔵 低｜[工具描述投毒] 工具描述異常冗長

長描述在功能複雜的工具上很常見，但也是把指令埋在人不會滑到的位置的手法。若前面沒有其他命中，通常不必緊張。

> 證據：`connectors/browserbase/src/tools/agent-runs.ts｜長度 1669 字`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`connectors/_template/src/bridge.ts、connectors/apple-shortcuts/__tests__/run-input-path.test.ts、connectors/apple-shortcuts/src/index.ts、connectors/browser-automation/src/path-safety.ts、connectors/browser-automation/test/eval-gate-and-schemes.test.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`connectors/_template/src/bridge.ts、connectors/_template/src/types.ts、connectors/apple-shortcuts/__tests__/timeout.test.ts、connectors/apple-shortcuts/src/index.ts、connectors/apple-shortcuts/src/logger.ts`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`connectors/apple-shortcuts/__tests__/timeout.test.ts、connectors/apple-shortcuts/src/index.ts、connectors/browser-automation/src/browser-client.ts、connectors/browser-automation/test/browser-client.test.ts、connectors/browser-automation/test/error-handling.test.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 3 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、connectors/office/AGENTS.md（Agent 指令（AGENTS.md 慣例））`

### ⚪ 資訊｜[權限] 判定用途：瀏覽器／網頁自動化

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 2 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-26`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.mindstone/mcp-server-google-analytics`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 10｜fork 4｜語言 TypeScript｜建立 2026-04-08｜最後推送 2026-08-26

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*