# MCP 安檢報告：arcadia-finance/mcp-server

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `arcadia-finance/mcp-server` |
| 專案說明 | MCP server for Arcadia Finance. Manage concentrated liquidity positions with bui |
| 星數 / Fork | ⭐ 5 / 1 |
| 最後更新 | 2026-08-10 |
| 授權 | GNU Affero General Public License v3.0 |
| npm 套件 | `@arcadia-finance/mcp-server` |
| 已掃描檔案 | 115 個 |
| 檢查時間 | 2026-08-14 21:29 |

## 風險摘要

🟡 中 1　🔵 低 2　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[權限] 會連往 14 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.arcadia.finance、arcadia.finance、custom-base-rpc.example.com、custom-op-rpc.example.com、custom-uni-rpc.example.com、dashboard.tenderly.co、glama.ai、mainnet.base.org、mainnet.optimism.io、mainnet.unichain.org…`

### 🔵 低｜[供應鏈] 有 17 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@modelcontextprotocol/sdk@^1.12.0、express@^5.2.1、express-rate-limit@^8.3.1、viem@^2.0.0、zod@^3.23.0、@eslint/js@^9.0.0…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「一般用途（未能明確判定）」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`src/clients/api.ts、src/config/chains.test.ts、src/config/chains.ts、src/index.ts、src/tools/dev/send.test.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 4 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、llms.txt（給模型讀的站點說明（llms.txt））、skills/clamm-liquidity/SKILL.md（Agent Skill 指令（SKILL.md））、skills/openclaw/SKILL.md（Agent Skill 指令（SKILL.md））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 60 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：一般用途（未能明確判定）

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 4 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-10`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.arcadia-finance/mcp-server`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 5｜fork 1｜語言 TypeScript｜建立 2026-03-03｜最後推送 2026-08-10

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*