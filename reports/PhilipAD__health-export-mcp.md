# MCP 安檢報告：PhilipAD/health-export-mcp

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `PhilipAD/health-export-mcp` |
| 專案說明 | Apple Health MCP server: query 190 HealthKit metrics from Claude, ChatGPT, Curso |
| 星數 / Fork | ⭐ 2 / 1 |
| 最後更新 | 2026-07-27 |
| 授權 | MIT License |
| npm 套件 | `health-export-mcp` |
| 已掃描檔案 | 19 個 |
| 檢查時間 | 2026-07-30 22:10 |

## 風險摘要

🟠 高 2　🟡 中 1　🔵 低 1　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 會讀寫本機檔案（超出宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。但它自述是「一般用途（未能明確判定）」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`apply-mcp-config.mjs、apply-mcp-config.test.mjs、healthstore.mjs、receiver.mjs、receiver.test.mjs`

### 🟠 高｜[權限] ⚠ 會執行外部指令 / 開子行程（超出宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。但它自述是「一般用途（未能明確判定）」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`apply-mcp-config.test.mjs、test/integration.mjs`

### 🟡 中｜[權限] 會連往 8 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`apps.apple.com、evil.example.com、glama.ai、insiders.vscode.dev、opencode.ai、smithery.ai、static.modelcontextprotocol.io、www.healthexport.dev`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「一般用途（未能明確判定）」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`apply-mcp-config.mjs、apply-mcp-config.test.mjs、healthstore.mjs、receiver.mjs、server.mjs`

### ⚪ 資訊｜[代理指令檔] 已掃描 2 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、llms.txt（給模型讀的站點說明（llms.txt））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 20 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：一般用途（未能明確判定）

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 4 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-27`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.PhilipAD/health-export-mcp`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 2｜fork 1｜語言 JavaScript｜建立 2026-06-27｜最後推送 2026-07-27

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*