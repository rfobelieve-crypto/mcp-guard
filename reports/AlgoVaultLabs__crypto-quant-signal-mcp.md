# MCP 安檢報告：AlgoVaultLabs/crypto-quant-signal-mcp

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `AlgoVaultLabs/crypto-quant-signal-mcp` |
| 專案說明 | AI trading brain for crypto perps — composite signals, funding rate arb scanning |
| 星數 / Fork | ⭐ 5 / 4 |
| 最後更新 | 2026-08-11 |
| 授權 | MIT License |
| npm 套件 | `crypto-quant-signal-mcp` |
| 已掃描檔案 | 402 個 |
| 檢查時間 | 2026-08-11 21:48 |

## 風險摘要

🟠 高 2　🟡 中 2　🔵 低 2　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 會讀寫本機檔案（超出宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。但它自述是「第三方 API 串接」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`.github/workflows/deploy.yml、audits/knowledge-shape-snapshot-2026-05-18.json`

### 🟠 高｜[權限] ⚠ 會執行外部指令 / 開子行程（超出宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。但它自述是「第三方 API 串接」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`audits/ACTIVATION-FUNNEL-AUDIT-W1-funnel-leak-detector.py`

### 🟡 中｜[代理指令檔] 指令檔提及金鑰或 SSH 路徑

若這份指令的主題本來就是金鑰管理屬正常；否則要問：一份操作說明為什麼需要讓模型知道私鑰放在哪裡。

> 證據：`.claude/commands/geo-decide.md｜「…decision from Postgres (the cross-host boundary): ``` ssh -i ~/.ssh/algovault_deploy root@204.168.185.24 \ "docker exec crypto-quant-…」`

### 🟡 中｜[權限] 會連往 14 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`algovault.com、api.algovault.com、api.babyblueviper.com、avatars.githubusercontent.com、basescan.org、cdn.tailwindcss.com、checkout.stripe.com、crypto-quant-signal-mcp--algovault.run.tools、docs.stripe.com、fonts.googleapis.com…`

### 🔵 低｜[供應鏈] 有 47 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@anthropic-ai/sdk@^0.96.0、@buildersgarden/siwa@^0.0.24、@circle-fin/x402-batching@^3.2.0、@coinbase/x402@^2.1.0、@modelcontextprotocol/sdk@^1.12.1、@slicekit/erc8128@^0.3.3…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「第三方 API 串接」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/postgres-lane.yml、audits/ACTIVATION-FUNNEL-AUDIT-W1-funnel-leak-detector.py、audits/api-erc-8004-reputation-shape-snapshot-2026-05-16.json、examples/governance-handoff/demo.py`

### ⚪ 資訊｜[代理指令檔] 已掃描 2 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/commands/geo-decide.md（AI 客戶端設定目錄下的指令檔）、landing/llms.txt（給模型讀的站點說明（llms.txt））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 0 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：第三方 API 串接

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 1 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-11`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.AlgoVaultFi/crypto-quant-signal-mcp`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 5｜fork 4｜語言 TypeScript｜建立 2026-04-04｜最後推送 2026-08-11

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*