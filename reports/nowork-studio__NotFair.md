# MCP 安檢報告：nowork-studio/NotFair

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `nowork-studio/NotFair` |
| 專案說明 | Open-source SEO, GEO, and marketing skills for AI agents. |
| 星數 / Fork | ⭐ 3928 / 496 |
| 最後更新 | 2026-10-09 |
| 授權 | MIT License |
| 已掃描檔案 | 280 個 |
| 檢查時間 | 2026-10-13 02:28 |

## 風險摘要

🟠 高 1　🟡 中 1　🔵 低 3　⚪ 資訊 6

## 詳細發現

### 🟠 高｜[權限] ⚠ 會執行外部指令 / 開子行程（超出宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。但它自述是「文件／知識檢索」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`seo/seo-analysis/scripts/_gcloud.py、seo/seo-analysis/scripts/analyze_gsc.py、seo/seo-analysis/scripts/list_gsc_sites.py、seo/seo-analysis/scripts/preflight.py、seo/seo-analysis/scripts/url_inspection.py`

### 🟡 中｜[權限] 會連往 35 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`acme-saas.com、agent-plugins.org、api.google.com、app.contentful.com、bakersjournal.com、cdn.contentful.com、cloud.google.com、cms.example.com、console.cloud.google.com、developers.facebook.com…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「文件／知識檢索」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`scripts/notfair-change-watch.sh、scripts/notfair-content-calendar.py、seo/broken-link-checker/scripts/checker.py、seo/seo-analysis/scripts/_gcloud.py、seo/seo-analysis/scripts/_http.py`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「文件／知識檢索」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`scripts/notfair-content-calendar.py、seo/seo-analysis/scripts/_gcloud.py、seo/seo-analysis/scripts/_uid.py、seo/seo-analysis/scripts/cms_detect.py、seo/seo-analysis/scripts/fetch_contentful_content.py`

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 已掃描 49 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、skills/backlink-audit/SKILL.md（Agent Skill 指令（SKILL.md））、skills/broken-link-checker/SKILL.md（Agent Skill 指令（SKILL.md））、skills/competitor-pages/SKILL.md（Agent Skill 指令（SKILL.md））、skills/content-planner/SKILL.md（Agent Skill 指令（SKILL.md））、skills/content-writer/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 4 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：文件／知識檢索

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、TOKEN`

### ⚪ 資訊｜[維護] 最近 3 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-10-09`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 3928｜fork 496｜語言 Python｜建立 2026-03-27｜最後推送 2026-10-09

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*