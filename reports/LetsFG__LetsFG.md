# MCP 安檢報告：LetsFG/LetsFG

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `LetsFG/LetsFG` |
| 專案說明 | Agent-native flight & hotel search and booking — MCP server, CLI, and Python/JS  |
| 星數 / Fork | ⭐ 1963 / 132 |
| 最後更新 | 2026-08-27 |
| 授權 | Other |
| 已掃描檔案 | 137 個 |
| 檢查時間 | 2026-09-01 23:06 |

## 風險摘要

🟡 中 1　🔵 低 5　⚪ 資訊 5

## 詳細發現

### 🟡 中｜[權限] 會連往 49 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`agent.example.com、basemaps.cartocdn.com、booking.flyscoot.com、bookingportal.china-airlines.com、carrier.example.com、checknfly.co.uk、checkout.stripe.com、checkout.stripe.com.evil.com、checkout.stripe.com.evil.example、context7.com…`

### 🔵 低｜[工具描述投毒] 描述含「優先呼叫本工具」的措辭

這在正常 MCP 中很常見（引導模型選對工具），但也是投毒用來搶奪呼叫權的手法。請確認它引導的方向合理、且沒有附帶額外指令。

> 證據：`sdk/mcp/src/index.ts｜「Convert a city/airport name to IATA codes. Always call before search_flights if you only have a city name.」`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`preview/build_stubs.py、preview/run.py、sdk/python/google_checkout_live_sweep.py、sdk/python/letsfg/cli.py、sdk/python/letsfg/client.py`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`preview/run.py、sdk/js/src/auth.test.ts、sdk/js/src/auth.ts、sdk/js/src/cli.ts、sdk/js/src/index.ts`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`sdk/js/src/auth.ts、sdk/mcp/src/index.test.ts、tools/build-ranking.py`

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 已掃描 6 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、SKILL.md（Agent Skill 指令（SKILL.md））、agent-skills-contribution/packages/skills-catalog/skills/(tooling)/letsfg/SKILL.md（Agent Skill 指令（SKILL.md））、skills/flight-search/SKILL.md（Agent Skill 指令（SKILL.md））、skills/hotel-search/SKILL.md（Agent Skill 指令（SKILL.md））`

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 5 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-27`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1963｜fork 132｜語言 Python｜建立 2026-03-01｜最後推送 2026-08-27

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*