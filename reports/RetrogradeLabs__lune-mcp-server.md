# MCP 安檢報告：RetrogradeLabs/lune-mcp-server

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `RetrogradeLabs/lune-mcp-server` |
| 專案說明 | Official MCP server for Lune Research: search top-tier papers and methodology gu |
| 星數 / Fork | ⭐ 3 / 1 |
| 最後更新 | 2026-06-13 |
| 授權 | MIT License |
| npm 套件 | `@retrograde-labs/lune-mcp-server` |
| 已掃描檔案 | 57 個 |
| 檢查時間 | 2026-08-05 22:18 |

## 風險摘要

🟠 高 1　🟡 中 1　🔵 低 2　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 會執行外部指令 / 開子行程（超出宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。但它自述是「文件／知識檢索」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`tests/integration/full-stdio.test.ts`

### 🟡 中｜[權限] 會連往 12 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.luneresearch.com、chatgpt.com、claude.ai、claude.com、developers.openai.com、evil.example.com、json.schemastore.org、luneresearch.com、mcp.luneresearch.com、platform.openai.com…`

### 🔵 低｜[供應鏈] 有 14 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@modelcontextprotocol/sdk@^1.29.0、express@^5.2.1、jose@^4.15.9、ky@^2.0.2、redis@^6.0.0、zod@^4.4.3…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「文件／知識檢索」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`src/api/client.ts、src/auth/token.ts、src/auth/verify.ts、src/cache.ts、src/cli.ts`

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 34 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：文件／知識檢索

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 53 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-06-13`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 com.luneresearch/lune`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 3｜fork 1｜語言 TypeScript｜建立 2026-05-10｜最後推送 2026-06-13

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*