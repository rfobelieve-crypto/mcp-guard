# MCP 安檢報告：timescale/pg-aiguide

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `timescale/pg-aiguide` |
| 專案說明 | MCP server and Claude plugin for Postgres skills and documentation. Helps AI cod |
| 星數 / Fork | ⭐ 1805 / 102 |
| 最後更新 | 2026-06-26 |
| 授權 | Apache License 2.0 |
| npm 套件 | `@tigerdata/pg-aiguide` |
| 已掃描檔案 | 79 個 |
| 檢查時間 | 2026-08-03 22:11 |

## 風險摘要

🟠 高 2　🟡 中 1　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[代理指令檔] 指令檔要求下載並直接執行遠端腳本

叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——你稽核過的原始碼完全管不到它。

> 證據：`skills/ghost-database/SKILL.md｜「```bash curl -fsSL https://install.ghost.build | sh ```」`

### 🟠 高｜[代理指令檔] 指令檔要求下載並直接執行遠端腳本

叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——你稽核過的原始碼完全管不到它。

> 證據：`skills/ghost-database/SKILL.md｜「```powershell irm https://install.ghost.build/install.ps1 | iex ```」`

### 🟡 中｜[權限] 會連往 12 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`agentskills.io、biomejs.dev、docs.npmjs.com、ghcr.io、hub.docker.com、mcp.tigerdata.com、postgis.net、registry.modelcontextprotocol.io、static.modelcontextprotocol.io、tigerdata.com…`

### 🔵 低｜[供應鏈] 有 13 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@opentelemetry/api@^1.9.1、dotenv@^17.4.2、gray-matter@^4.0.3、migrate@^2.1.0、pg@^8.22.0、zod@^4.3.6…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`ingest/constants.py、ingest/postgres_docs.py、ingest/tiger_docs.py、ingest/utils/db.py、migrations/1756387543053-initial.js`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`ingest/postgres_docs.py`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`ingest/postgres_docs.py、ingest/tiger_docs.py`

### ⚪ 資訊｜[代理指令檔] 已掃描 12 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、rules/postgres-best-practices.mdc（Cursor 規則檔（.mdc））、skills/design-postgis-tables/SKILL.md（Agent Skill 指令（SKILL.md））、skills/design-postgres-tables/SKILL.md（Agent Skill 指令（SKILL.md））、skills/find-hypertable-candidates/SKILL.md（Agent Skill 指令（SKILL.md））、skills/ghost-database/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 21 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 38 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-06-26`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.timescale/pg-aiguide`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1805｜fork 102｜語言 Python｜建立 2025-07-23｜最後推送 2026-06-26

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*