# MCP 安檢報告：modelcontextprotocol/servers

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `modelcontextprotocol/servers` |
| 專案說明 | Model Context Protocol Servers |
| 星數 / Fork | ⭐ 88977 / 11302 |
| 最後更新 | 2026-07-26 |
| 授權 | Other |
| npm 套件 | `@modelcontextprotocol/servers`（registry 查無） |
| 已掃描檔案 | 122 個 |
| 檢查時間 | 2026-07-28 17:03 |

## 風險摘要

🟡 中 1　🔵 低 6　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[權限] 會連往 5 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.example.com、opencollective.com、proxy.example.com、registry.modelcontextprotocol.io、tidelift.com`

### 🔵 低｜[供應鏈] 有 4 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@modelcontextprotocol/server-everything@*、@modelcontextprotocol/server-memory@*、@modelcontextprotocol/server-filesystem@*、@modelcontextprotocol/server-sequential-thinking@*`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`scripts/release.py、src/filesystem/__tests__/startup-validation.test.ts、src/filesystem/__tests__/structured-content.test.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`scripts/release.py、src/filesystem/__tests__/directory-tree.test.ts、src/filesystem/__tests__/path-validation.test.ts、src/filesystem/__tests__/startup-validation.test.ts、src/filesystem/__tests__/structured-content.test.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`src/everything/__tests__/tools.test.ts、src/everything/tools/get-env.ts、src/everything/tools/gzip-file-as-resource.ts、src/everything/transports/sse.ts、src/everything/transports/streamableHttp.ts`

### 🔵 低｜[維護] 未處理 issue 偏多（686 則）

可能代表維護者回應不及，遇到問題時求助無門。

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 已掃描 2 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、src/everything/AGENTS.md（Agent 指令（AGENTS.md 慣例））`

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（@modelcontextprotocol/servers）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 102 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 2 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-26`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 88977｜fork 11302｜語言 TypeScript｜建立 2024-11-19｜最後推送 2026-07-26

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*