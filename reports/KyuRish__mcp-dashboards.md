# MCP 安檢報告：KyuRish/mcp-dashboards

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `KyuRish/mcp-dashboards` |
| 專案說明 | Turn your data into interactive dashboards inside any AI client - MCP Apps power |
| 星數 / Fork | ⭐ 43 / 7 |
| 最後更新 | 2026-07-12 |
| 授權 | Other |
| npm 套件 | `mcp-dashboards` |
| 已掃描檔案 | 48 個 |
| 檢查時間 | 2026-08-10 21:44 |

## 風險摘要

🟡 中 1　🔵 低 3　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[權限] 會連往 6 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`buymeacoffee.com、fonts.googleapis.com、opencollective.com、static.modelcontextprotocol.io、tidelift.com、your-host.com`

### 🔵 低｜[供應鏈] 有 31 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@modelcontextprotocol/ext-apps@^1.7.2、@modelcontextprotocol/sdk@^1.29.0、cors@^2.8.6、express@^5.2.1、ipaddr.js@^2.4.0、zod@^4.4.3…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`index.ts、preview-server.ts、server.ts、url-safety.ts、vite.config.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`preview-server.ts、server.ts`

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 39 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PASSWORD、TOKEN`

### ⚪ 資訊｜[維護] 最近 30 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-12`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.KyuRish/mcp-dashboards`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 43｜fork 7｜語言 TypeScript｜建立 2026-02-23｜最後推送 2026-07-12

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*