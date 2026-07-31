# MCP 安檢報告：mcparmory/registry

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `mcparmory/registry` |
| 專案說明 | Production-ready MCP servers for 70+ APIs — GitHub, Google, Notion, Jira & more. |
| 星數 / Fork | ⭐ 29 / 4 |
| 最後更新 | 2026-05-12 |
| 授權 | Other |
| 已掃描檔案 | 466 個 |
| 檢查時間 | 2026-07-31 22:09 |

## 風險摘要

🟡 中 3　🔵 低 2　⚪ 資訊 6

## 詳細發現

### 🟡 中｜[工具描述投毒] 描述中提及金鑰或 SSH 路徑

若這個工具本來就處理金鑰檔案屬正常；否則要問為什麼描述需要提到它。

> 證據：`servers/files-com/_models.py｜「Remote server SSH host key in OpenSSH format (as would appear in ~/.ssh/known_hosts). When provided, the server's host k」`

### 🟡 中｜[工具描述投毒] 描述中出現系統提示詞標記或字樣

描述裡出現 <system> 之類的標記，可能是想偽裝成系統訊息。請確認上下文。

> 證據：`servers/firecrawl/_models.py｜「System prompt for controlling JSON output generation behavior and formatting」`

### 🟡 中｜[權限] 會連往 103 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`a.klaviyo.com、about.gitlab.com、account.box.com、accounts.google.com、ahrefs.com、airtable.com、analyticsdata.googleapis.com、api.agentql.com、api.ahrefs.com、api.airtable.com…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`servers/agentql/_auth.py、servers/agentql/server.py、servers/ahrefs/_auth.py、servers/ahrefs/server.py、servers/airtable/_auth.py`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`servers/agentql/server.py、servers/ahrefs/_auth.py、servers/ahrefs/server.py、servers/airtable/_auth.py、servers/airtable/server.py`

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 80 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-05-12`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 com.mcparmory/google-analytics`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 29｜fork 4｜語言 Python｜建立 2026-03-23｜最後推送 2026-05-12

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*