# MCP 安檢報告：CryptoCultCurt/appfolio-mcp-server

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `CryptoCultCurt/appfolio-mcp-server` |
| 專案說明 | MCP (Model Context Protocol) Server for AI Agents to access the Appfolio Reporti |
| 星數 / Fork | ⭐ 9 / 5 |
| 最後更新 | 2026-01-12 |
| 授權 | ISC License |
| npm 套件 | `@fluegeldao/appfolio-mcp-server` |
| 已掃描檔案 | 112 個 |
| 檢查時間 | 2026-08-14 21:29 |

## 風險摘要

🟡 中 1　🔵 低 3　⚪ 資訊 6

## 詳細發現

### 🟡 中｜[維護] 約 7 個月沒有更新

更新頻率偏低，導入前先確認它仍相容你的 MCP 客戶端。

> 證據：`最後推送 2026-01-12`

### 🔵 低｜[供應鏈] 有 17 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@modelcontextprotocol/sdk@^1.17.2、@pipedream/sdk@^2.0.0-rc.11、@workos-inc/node@^7.66.0、axios@^1.6.7、bottleneck@^2.19.5、cors@^2.8.5…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「第三方 API 串接」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`dist/appfolio.js、dist/index-stytch.js、dist/index.js、dist/pipedream.js、src/appfolio.ts`

### 🔵 低｜[權限] 會連往 2 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`smithery.ai、stytch.com`

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 146 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：第三方 API 串接

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 ai.smithery/CryptoCultCurt-appfolio-mcp-server`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 9｜fork 5｜語言 TypeScript｜建立 2025-04-16｜最後推送 2026-01-12

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*