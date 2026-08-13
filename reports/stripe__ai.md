# MCP 安檢報告：stripe/ai

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `stripe/ai` |
| 專案說明 | One-stop shop for building AI-powered products and businesses with Stripe. |
| 星數 / Fork | ⭐ 1740 / 325 |
| 最後更新 | 2026-08-11 |
| 授權 | MIT License |
| 已掃描檔案 | 450 個 |
| 檢查時間 | 2026-08-13 21:46 |

## 風險摘要

🟡 中 1　🔵 低 4　⚪ 資訊 6

## 詳細發現

### 🟡 中｜[權限] 會連往 26 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`accessible.stripe.com、admin.corp.stripe.com、dashboard.stripe.com、docs.google.com、docs.stripe.com、eslint.org、feross.org、go.microsoft.com、hubble.corp.stripe.com、inaccessible.stripe.com…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`benchmarks/card-element-to-checkout/environment/init_products.py、benchmarks/card-element-to-checkout/environment/server/main.py、benchmarks/card-element-to-checkout/environment/server/server.py、benchmarks/card-element-to-checkout/grader/checkout_tests.py、benchmarks/card-element-to-checkout/solution/server/main.py`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`benchmarks/furever/environment/app/(dashboard)/settings/layout.tsx、benchmarks/furever/environment/scripts/setup-accounts.py、benchmarks/furever/grader/payments.py`

### 🔵 低｜[維護] 未處理 issue 偏多（79 則）

可能代表維護者回應不及，遇到問題時求助無門。

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 已掃描 35 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`providers/claude/plugin/skills/connect-recommend/SKILL.md（Agent Skill 指令（SKILL.md））、providers/claude/plugin/skills/stripe-apps/SKILL.md（Agent Skill 指令（SKILL.md））、providers/claude/plugin/skills/stripe-best-practices/SKILL.md（Agent Skill 指令（SKILL.md））、providers/claude/plugin/skills/stripe-directory/SKILL.md（Agent Skill 指令（SKILL.md））、providers/claude/plugin/skills/stripe-docs/SKILL.md（Agent Skill 指令（SKILL.md））、providers/claude/plugin/skills/stripe-projects/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 64 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 2 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-11`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1740｜fork 325｜語言 TypeScript｜建立 2024-11-11｜最後推送 2026-08-11

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*