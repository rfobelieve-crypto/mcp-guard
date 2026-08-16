# MCP 安檢報告：modelcontextprotocol/registry

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `modelcontextprotocol/registry` |
| 專案說明 | A community driven registry service for Model Context Protocol (MCP) servers. |
| 星數 / Fork | ⭐ 7158 / 947 |
| 最後更新 | 2026-08-12 |
| 授權 | Other |
| 已掃描檔案 | 213 個 |
| 檢查時間 | 2026-08-16 21:18 |

## 風險摘要

🟡 中 1　🔵 低 1　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[權限] 會連往 62 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`Registry.Example.COM、accounts.google.com、acme-v02.api.letsencrypt.org、airtable.com、api-a.example.com、api-b.example.com、api-c.example.com、api.allversions.com、api.deleted.com、api.example.com…`

### 🔵 低｜[維護] 未處理 issue 偏多（135 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 2 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.github/copilot-instructions.md（GitHub Copilot 指令）、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 187 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 4 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-12`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 ai.com.mcp/registry`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 7158｜fork 947｜語言 Go｜建立 2025-02-05｜最後推送 2026-08-12

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*