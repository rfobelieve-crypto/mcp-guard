# MCP 安檢報告：exa-labs/exa-mcp-server

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `exa-labs/exa-mcp-server` |
| 專案說明 | Exa MCP for web search and web crawling! |
| 星數 / Fork | ⭐ 4880 / 375 |
| 最後更新 | 2026-08-17 |
| 授權 | MIT License |
| npm 套件 | `exa-mcp-server` |
| 已掃描檔案 | 76 個 |
| 檢查時間 | 2026-08-17 21:26 |

## 風險摘要

🟡 中 2　🔵 低 2　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "npm run build:stdio"`

### 🟡 中｜[權限] 會連往 18 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`a.com、agent-plugins.org、api.agnost.ai、auth.exa.ai、b.com、client.example、dashboard.exa.ai、developers.openai.com、docs.exa.ai、dotenvx.com…`

### 🔵 低｜[供應鏈] 有 13 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@modelcontextprotocol/sdk@^1.12.1、agnost@^0.2.0、exa-js@^2.16.0、jose@^6.2.2、mcp-handler@^1.0.4、zod@^3.22.4…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`api/mcp.ts、api/well-known-oauth-protected-resource.ts、api/well-known-openai-apps-challenge.ts、src/stdio.ts、src/tools/config.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 2 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`skills/exa-agent/SKILL.md（Agent Skill 指令（SKILL.md））、skills/search/SKILL.md（Agent Skill 指令（SKILL.md））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 29 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：瀏覽器／網頁自動化

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-17`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 ai.exa/exa`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 4880｜fork 375｜語言 TypeScript｜建立 2024-11-27｜最後推送 2026-08-17

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*