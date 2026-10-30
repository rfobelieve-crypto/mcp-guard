# MCP 安檢報告：aks129/HealthClawGuardrails

> **結論：🔴 不要安裝**　發現 1 項嚴重問題，安裝風險無法接受。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `aks129/HealthClawGuardrails` |
| 專案說明 | Open-source guardrails between AI agents and FHIR clinical data — PHI redaction, |
| 星數 / Fork | ⭐ 31 / 12 |
| 最後更新 | 2026-10-28 |
| 授權 | MIT License |
| npm 套件 | `healthclaw-guardrails-mcp`（registry 查無） |
| 已掃描檔案 | 415 個 |
| 檢查時間 | 2026-10-30 00:42 |

## 風險摘要

🔴 嚴重 1　🟠 高 2　🟡 中 1　🔵 低 3　⚪ 資訊 8

## 詳細發現

### 🔴 嚴重｜[工具描述投毒] 原始碼含雙向覆寫字元

bidi 覆寫字元會讓「你在畫面上讀到的程式碼」與「編譯器實際讀到的」順序不同，是 Trojan Source（CVE-2021-42574）的手法。除了處理雙向文字的函式庫，正常原始碼沒有理由出現它們。

> 證據：`careagents/static/checkin_answer.js｜位置 9711｜U+202A`

### 🟠 高｜[權限] ⚠ 會讀寫本機檔案（超出宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。但它自述是「第三方 API 串接」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`.github/workflows/careagents-deploy.yml、.github/workflows/careagents-drift.yml、.github/workflows/ci.yml、.github/workflows/pr-risk.yml、.github/workflows/prod-watch.yml`

### 🟠 高｜[權限] ⚠ 會執行外部指令 / 開子行程（超出宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。但它自述是「第三方 API 串接」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`deploy/careagents/imessage_relay.py、openclaw/bot.py`

### 🟡 中｜[權限] 會連往 50 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.anthropic.com、api.bland.ai、api.connect.fastenhealth.com、api.elevenlabs.io、api.medplum.com、api.openai.com、api.resend.com、api.sendblue.co、api.telegram.org、api.twilio.com…`

### 🔵 低｜[供應鏈] 有 15 個依賴未鎖定版本

依賴沒有釘死版本，代表未來安裝時拉到的新版可能與你稽核過的內容不同。

> 證據：`alembic>=1.16.5,<2、anthropic>=0.49.0、email-validator>=2.2.0、fhirpathpy>=2.2.1,<3、flask>=3.1.0、flask-sqlalchemy>=3.1.1…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「第三方 API 串接」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/careagents-deploy.yml、.github/workflows/careagents-drift.yml、.github/workflows/pr-risk.yml、.github/workflows/prod-watch.yml、api/index.py`

### 🔵 低｜[維護] 未處理 issue 偏多（80 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 16 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`GEMINI.md（Gemini CLI 指令）、docs/quickstarts/claude.md（Claude Code 專案指令（CLAUDE.md））、skills/check-sources/SKILL.md（Agent Skill 指令（SKILL.md））、skills/curatr/SKILL.md（Agent Skill 指令（SKILL.md））、skills/fasten-connect/SKILL.md（Agent Skill 指令（SKILL.md））、skills/fhir-r6-guardrails/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（healthclaw-guardrails-mcp）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[供應鏈] PyPI 上查無此套件（healthclaw-guardrails）

原始碼宣告了套件名但 PyPI 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[權限] 判定用途：第三方 API 串接

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 1 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-10-28`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.aks129/healthclaw-guardrails`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 31｜fork 12｜語言 Python｜建立 2025-03-31｜最後推送 2026-10-28

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*