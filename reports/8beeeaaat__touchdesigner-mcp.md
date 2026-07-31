# MCP 安檢報告：8beeeaaat/touchdesigner-mcp

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `8beeeaaat/touchdesigner-mcp` |
| 專案說明 | MCP server for TouchDesigner |
| 星數 / Fork | ⭐ 457 / 48 |
| 最後更新 | 2026-07-31 |
| 授權 | MIT License |
| npm 套件 | `touchdesigner-mcp-server` |
| 已掃描檔案 | 152 個 |
| 檢查時間 | 2026-07-31 22:10 |

## 風險摘要

🟠 高 1　🟡 中 2　🔵 低 5　⚪ 資訊 8

## 詳細發現

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「程式碼／版控工具」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`td/import_modules.py、td/modules/mcp/services/api_service.py、td/modules/utils/serialization.py`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 10 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`docs.derivative.ca、docs.github.com、feross.org、host.docker.internal、json.schemastore.org、opencollective.com、paulmillr.com、static.modelcontextprotocol.io、tidelift.com、www.patreon.com`

### 🔵 低｜[供應鏈] 有 5 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@modelcontextprotocol/core@^2.0.0、@modelcontextprotocol/express@^2.0.0、@modelcontextprotocol/node@^2.0.0、@modelcontextprotocol/server@^2.0.0、@modelcontextprotocol/client@^2.0.0`

### 🔵 低｜[供應鏈] 有 1 個依賴未鎖定版本

依賴沒有釘死版本，代表未來安裝時拉到的新版可能與你稽核過的內容不同。

> 證據：`PyYAML>=6.0`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.claude/hooks/integration-test-guard.mjs、scripts/syncMcpServerVersions.ts、tests/e2e/helpers/serverProcess.ts、tests/unit/genHandlers.test.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.claude/hooks/integration-test-guard.mjs、scripts/formatPreview.ts、scripts/measureFormatterImpact.ts、scripts/showDetailedNodes.ts、src/api/index.yml`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`td/genHandlers.js、td/import_modules.py、tests/unit/genHandlers.test.ts、tests/unit/toolListingsSync.test.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 9 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/agents/release-manager.md（AI 客戶端設定目錄下的指令檔）、.claude/skills/integration-test-guard/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/prepare-release/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/prepare-release/references/changelog-format.md（AI 客戶端設定目錄下的指令檔）、.claude/skills/prepare-release/references/version-policy.md（AI 客戶端設定目錄下的指令檔）、.claude/skills/release-test-audit/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[供應鏈] PyPI 上查無此套件（touchdesigner-mcp）

原始碼宣告了套件名但 PyPI 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 19 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-31`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.8beeeaaat/touchdesigner-mcp-server`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 457｜fork 48｜語言 TypeScript｜建立 2025-04-13｜最後推送 2026-07-31

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*