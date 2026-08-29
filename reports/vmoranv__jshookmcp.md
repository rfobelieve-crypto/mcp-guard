# MCP 安檢報告：vmoranv/jshookmcp

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `vmoranv/jshookmcp` |
| 專案說明 | js hook toolkit that all you need |
| 星數 / Fork | ⭐ 1954 / 455 |
| 最後更新 | 2026-08-27 |
| 授權 | GNU Affero General Public License v3.0 |
| npm 套件 | `@jshookmcp/jshook` |
| 已掃描檔案 | 400 個 |
| 檢查時間 | 2026-08-29 03:08 |

## 風險摘要

🟠 高 2　🟡 中 2　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[供應鏈] 安裝時會自動執行腳本：postinstall

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"postinstall": "node scripts/postinstall.cjs"`

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「瀏覽器／網頁自動化」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`scripts/runtime-probes/phases/browser/core.mjs、scripts/runtime-probes/phases/maintenance-workflow.mjs、src/modules/analyzer/SecurityCodeAnalyzer.ts、src/modules/collector/DOMInspector.ts、src/modules/detector/ObfuscationDetector.ts`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 14 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`afdian.com、api.dart.dev、api.flutter.dev、developer.android.com、docs.flutter.dev、docs.renovatebot.com、eldstal.se、example.invalid、fonts.googleapis.com、fonts.gstatic.com…`

### 🔵 低｜[供應鏈] 有 36 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@alexaltea/capstone-js@^5.0.9、@babel/generator@^8.0.0、@babel/parser@^8.0.0、@babel/traverse@^8.0.0、@babel/types@^8.0.0、@huggingface/tokenizers@^0.1.3…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`docs/.vitepress/shared.ts、scripts/audit-runtime-probes.mjs、scripts/audit-tools.mjs、scripts/generate-domains-index.mjs、scripts/generate-metadata.mjs`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`packages/extension-sdk/src/bridges/shared.ts、scripts/build.mjs、scripts/generate-domains-index.mjs、scripts/generate-metadata.mjs、scripts/generate-vitepress-reference.mjs`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「瀏覽器／網頁自動化」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`scripts/count-tools.js、scripts/count-tools.mjs、scripts/generate-domains-index.mjs、scripts/runtime-probes/phases/browser/page-interaction.mjs、scripts/runtime-probes/phases/runtime-observability/console-intercept-jsdom.mjs`

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 74 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：瀏覽器／網頁自動化

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 2 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-27`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.vmoranv/jshookmcp`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1954｜fork 455｜語言 TypeScript｜建立 2026-02-21｜最後推送 2026-08-27

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*