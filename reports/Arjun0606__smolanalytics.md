# MCP 安檢報告：Arjun0606/smolanalytics

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `Arjun0606/smolanalytics` |
| 專案說明 | open-source web + product analytics in one Go binary. ask your data in plain eng |
| 星數 / Fork | ⭐ 3 / 1 |
| 最後更新 | 2026-07-28 |
| 授權 | MIT License |
| 已掃描檔案 | 241 個 |
| 檢查時間 | 2026-07-28 17:11 |

## 風險摘要

🟠 高 1　🟡 中 1　🔵 低 1　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[代理指令檔] 指令檔要求下載並直接執行遠端腳本

叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——你稽核過的原始碼完全管不到它。

> 證據：`internal/api/llms.txt｜「…TE_KEY=<key> ghcr.io/arjun0606/smolanalytics:latest serve` - binary: `curl -fsSL https://raw.githubusercontent.com/Arjun0606/smolanalytics/main/install.sh | sh`」（另 1 個檔案有相同內容）`

### 🟡 中｜[權限] 會連往 28 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`accounts.google.com、chat.example.com、chatgpt.com、claude.ai、download.db-ip.com、eu.posthog.com、glama.ai、google.com、hooks.example.com、hooks.slack.com…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/mcp-publish.yml、internal/api/auth.go、internal/paths/paths_test.go、internal/store/file/file_test.go、internal/store/segment/deleteuser_test.go`

### ⚪ 資訊｜[代理指令檔] 已掃描 4 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、docs/agents.md（Agent 指令（AGENTS.md 慣例））、internal/api/llms.txt（給模型讀的站點說明（llms.txt））、llms.txt（給模型讀的站點說明（llms.txt））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 5 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-28`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.Arjun0606/smolanalytics`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 3｜fork 1｜語言 Go｜建立 2026-06-26｜最後推送 2026-07-28

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*