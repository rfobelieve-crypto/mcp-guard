# MCP 安檢報告：Vrun-design/openflowkit

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `Vrun-design/openflowkit` |
| 專案說明 | 100% Free, Open-source local-first AI diagramming for architecture diagrams and  |
| 星數 / Fork | ⭐ 721 / 153 |
| 最後更新 | 2026-08-19 |
| 授權 | MIT License |
| npm 套件 | `openflowkit`（registry 查無） |
| 已掃描檔案 | 402 個 |
| 檢查時間 | 2026-08-20 21:31 |

## 風險摘要

🟠 高 1　🟡 中 3　🔵 低 2　⚪ 資訊 8

## 詳細發現

### 🟠 高｜[權限] ⚠ 會讀寫本機檔案（超出宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。但它自述是「第三方 API 串接」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`public/sw.js、scripts/analyze-bundle.mjs、scripts/benchmark-harness.mjs、scripts/benchmark-summary.mjs、scripts/check-benchmark-results.mjs`

### 🟡 中｜[代理指令檔] 指令檔出現系統訊息標記

文字裡插入 <system> 這類標記，常見目的是讓自己的內容看起來像是客戶端下達的系統指令，藉此取得更高的服從度。

> 證據：`public/llms.txt｜「…dard rectangle. - `[decision]`: Diamond shape for logic branching. - `[system]`: Hexagon shape. - `[note]`: A sticky note appearance. - `[browser]`:…」`

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "node -e "if (process.env.CI) process.exit(0)" && husky || true"`

### 🟡 中｜[權限] 會連往 11 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.example.com、app.openflowkit.com、cdn.simpleicons.org、docs.openflowkit.com、openflowkit.com、simpleicons.org、static.modelcontextprotocol.io、us.i.posthog.com、www.figma.com、www.sitemaps.org…`

### 🔵 低｜[供應鏈] 有 61 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@google/genai@^1.40.0、@mermaid-js/layout-elk@^0.2.1、@xyflow/react@^12.10.1、d3-shape@^3.2.0、elkjs@^0.11.0、framer-motion@^12.34.0…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「第三方 API 串接」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`mcp-server/src/lib/viewerUrl.ts、package.json、playwright.config.ts、scripts/check-bundle-budget.mjs、signaling-server/server.js`

### ⚪ 資訊｜[代理指令檔] 已掃描 1 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`public/llms.txt（給模型讀的站點說明（llms.txt））`

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（openflowkit）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 55 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：第三方 API 串接

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 2 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-19`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.Vrun-design/openflowkit-mcp`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 721｜fork 153｜語言 TypeScript｜建立 2026-02-10｜最後推送 2026-08-19

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*