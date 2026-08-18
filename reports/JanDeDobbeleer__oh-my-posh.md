# MCP 安檢報告：JanDeDobbeleer/oh-my-posh

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `JanDeDobbeleer/oh-my-posh` |
| 專案說明 | The most customisable and low-latency cross platform/shell prompt renderer |
| 星數 / Fork | ⭐ 23306 / 2776 |
| 最後更新 | 2026-08-18 |
| 授權 | MIT License |
| 已掃描檔案 | 405 個 |
| 檢查時間 | 2026-08-18 21:23 |

## 風險摘要

🟠 高 1　🟡 中 2　🔵 低 2　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「桌面／終端控制」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`src/cli/dsc/shell.go、src/cli/dsc/shell_test.go`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 25 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`aka.ms、api.brewfather.app、bazel.build、cdn.ohmyposh.dev、containers.dev、discord.com、docs.bazel.build、docs.microsoft.com、en.wikipedia.org、example.awsapps.com…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/binary_size_report.yml、src/gitstatus/objectstore.go`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/homebrew.yml`

### ⚪ 資訊｜[代理指令檔] 已掃描 18 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.agents/skills/ast-grep/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/code-changes/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/conventional-commit/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/golang/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/markdown/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/powershell/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 0 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：桌面／終端控制

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-18`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 dev.ohmyposh/validator`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 23306｜fork 2776｜語言 Go｜建立 2019-03-13｜最後推送 2026-08-18

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*