# MCP 安檢報告：apify/apify-mcp-server

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `apify/apify-mcp-server` |
| 專案說明 | The Apify MCP server enables your AI agents to extract data from social media, s |
| 星數 / Fork | ⭐ 5982 / 250 |
| 最後更新 | 2026-09-04 |
| 授權 | MIT License |
| npm 套件 | `@apify/actors-mcp-server` |
| 已掃描檔案 | 356 個 |
| 檢查時間 | 2026-09-04 22:51 |

## 風險摘要

🟡 中 1　🔵 低 5　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[權限] 會連往 44 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`a.com、actor.example、actorpub.apify.actor、api.apify.com、apify-image-uploads-prod.s3.amazonaws.com、apify-image-uploads-prod.s3.us-east-1.amazonaws.com、apify.com、b.com、baldasseva--storybook-mcp.apify.actor、claude.ai…`

### 🔵 低｜[供應鏈] 有 31 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@apify/datastructures@^2.0.3、@apify/log@^2.5.16、@apify/utilities@^2.25.1、@modelcontextprotocol/ext-apps@^1.1.2、@segment/analytics-node@^2.3.0、@sentry/node@^10.38.0…`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/scripts/before-beta-release.js、evals/mcp_agent/run_mcp_agent_evals.ts、scripts/dev_standby.js、tests/e2e/protocol_v1.test.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/_conformance_tests.yaml、evals/config.ts、evals/create_dataset.ts、evals/evaluation_utils.ts、evals/mcp_agent/claude_agent.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`evals/mcp_agent/export_dataset.ts、src/web/build.js、src/web/src/utils/mock-openai.ts、tests/unit/resources.service.test.ts`

### 🔵 低｜[維護] 未處理 issue 偏多（140 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 12 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/agents/mcpc-tester.md（AI 客戶端設定目錄下的指令檔）、.claude/skills/bug-triage/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/creating-mcp-agent-evals/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/creating-mcp-agent-evals/reference.md（AI 客戶端設定目錄下的指令檔）、.claude/skills/dig/SKILL.md（Agent Skill 指令（SKILL.md））、AGENTS.md（Agent 指令（AGENTS.md 慣例））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 223 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：瀏覽器／網頁自動化

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-09-04`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 com.apify/apify-mcp-server`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 5982｜fork 250｜語言 TypeScript｜建立 2025-01-02｜最後推送 2026-09-04

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*