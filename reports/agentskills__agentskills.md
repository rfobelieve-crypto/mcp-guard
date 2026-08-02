# MCP 安檢報告：agentskills/agentskills

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `agentskills/agentskills` |
| 專案說明 | Specification and documentation for Agent Skills |
| 星數 / Fork | ⭐ 23761 / 1660 |
| 最後更新 | 2026-07-10 |
| 授權 | Apache License 2.0 |
| npm 套件 | `agentskills`（registry 查無） |
| 已掃描檔案 | 25 個 |
| 檢查時間 | 2026-08-02 21:56 |

## 風險摘要

🟡 中 1　🔵 低 1　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[權限] 會連往 56 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`agentman.ai、ampcode.com、autohand.ai、block.github.io、bub.build、claude.ai、code.claude.com、code.visualstudio.com、commandcode.ai、cursor.com…`

### 🔵 低｜[維護] 未處理 issue 偏多（56 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 2 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`docs/CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、skills-ref/CLAUDE.md（Claude Code 專案指令（CLAUDE.md））`

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（agentskills）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 45 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：文件／知識檢索

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[維護] 最近 24 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-10`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 ai.com.mcp/skills-search`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 23761｜fork 1660｜語言 Python｜建立 2025-12-16｜最後推送 2026-07-10

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*