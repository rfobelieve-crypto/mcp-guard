# MCP 安檢報告：t8y2/dbx

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `t8y2/dbx` |
| 專案說明 | 20 MB lightweight cross-platform database client for 70+ databases, including My |
| 星數 / Fork | ⭐ 12912 / 1249 |
| 最後更新 | 2026-08-01 |
| 授權 | Apache License 2.0 |
| npm 套件 | `dbx` |
| 已掃描檔案 | 426 個 |
| 檢查時間 | 2026-08-01 21:56 |

## 風險摘要

🟠 高 2　🟡 中 2　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[供應鏈] npm 套件標示的倉庫與實際來源不一致

套件明確指向的 repo 跟我們稽核的這個不是同一個。這可能是改名／monorepo，也可能是仿冒（typosquatting），需人工確認。

> 證據：`npm repository=git+https://github.com/samt/node-dbx.git｜稽核對象=t8y2/dbx`

### 🟠 高｜[權限] ⚠ 會執行外部指令 / 開子行程（超出宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。但它自述是「資料庫存取」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`.github/scripts/bump-agent-versions.mjs、.github/scripts/bump-jdbc-plugin-version.mjs、.github/scripts/check-jdbc-plugin-version.mjs、.github/scripts/i18n-autofill.mjs、.github/scripts/issue-commands.mjs`

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "husky"`

### 🟡 中｜[權限] 會連往 17 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.adoptium.net、api.changed.example.com、api.cloudflare.com、api.cnb.cool、api.deepseek.com、api.example.com、api.github.test、cnb.cool、dbx.example.com、dbxio.com…`

### 🔵 低｜[供應鏈] 有 71 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@babel/runtime@^7.29.7、@codemirror/autocomplete@^6.20.2、@codemirror/commands@^6.10.3、@codemirror/lang-html@^6.4.11、@codemirror/lang-json@^6.0.2、@codemirror/lang-sql@^6.10.0…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「資料庫存取」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/scripts/backfill-similar-issues.mjs、.github/scripts/bump-agent-versions.mjs、.github/scripts/cleanup-cnb-releases.mjs、.github/scripts/i18n-autofill.mjs、.github/scripts/issue-commands.mjs`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「資料庫存取」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/scripts/database-issue-catalog.mjs、.github/scripts/label-issue-database.mjs、.github/scripts/label-issue-database.test.mjs、.github/scripts/label-pull-request.mjs、.github/scripts/suggest-similar-issues.mjs`

### 🔵 低｜[維護] 未處理 issue 偏多（1130 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 2 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`docs/public/llms.txt（給模型讀的站點說明（llms.txt））、skills/dbx/SKILL.md（Agent Skill 指令（SKILL.md））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 1224 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：資料庫存取

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-01`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.t8y2/dbx`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 12912｜fork 1249｜語言 Rust｜建立 2026-04-29｜最後推送 2026-08-01

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*