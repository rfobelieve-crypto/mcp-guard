# MCP 安檢報告：bytedance/UI-TARS-desktop

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `bytedance/UI-TARS-desktop` |
| 專案說明 | The Open-Source Multimodal AI Agent Stack: Connecting Cutting-Edge AI Models and |
| 星數 / Fork | ⭐ 38708 / 3909 |
| 最後更新 | 2026-08-05 |
| 授權 | Apache License 2.0 |
| npm 套件 | `monorepo` |
| 已掃描檔案 | 472 個 |
| 檢查時間 | 2026-08-27 00:28 |

## 風險摘要

🟠 高 2　🟡 中 3　🔵 低 5　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[供應鏈] npm 套件標示的倉庫與實際來源不一致

套件明確指向的 repo 跟我們稽核的這個不是同一個。這可能是改名／monorepo，也可能是仿冒（typosquatting），需人工確認。

> 證據：`npm repository=git+ssh://git@github.com/mariuslundgard/monorepo.git｜稽核對象=bytedance/UI-TARS-desktop`

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「桌面／終端控制」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`multimodal/agent-tars/core/src/environments/local/browser/content-extractor.ts、multimodal/benchmark/content-extraction/src/strategies/optimized.ts、multimodal/benchmark/content-extraction/src/strategies/readability.ts`

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "husky"`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 36 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`agent-tars.com、beian.miit.gov.cn、browserbase.com、cli.github.com、console.volcengine.com、cpstest.click、developer.mozilla.org、eslint.org、feross.org、images.unsplash.com…`

### 🔵 低｜[供應鏈] 有 27 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`turbo@^2.4.4、@changesets/cli@^2.27.11、secretlint@^10.2.1、@commitlint/cli@^19.6.1、@commitlint/config-conventional@^19.6.0、@electron-toolkit/tsconfig@^1.0.1…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`apps/ui-tars/e2e/app.test.ts、apps/ui-tars/electron.vite.config.ts、apps/ui-tars/forge.config.ts、apps/ui-tars/playwright.config.ts、apps/ui-tars/src/main/env.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`apps/ui-tars/src/main/logger.ts、apps/ui-tars/src/main/remote/auth.ts、apps/ui-tars/src/renderer/src/components/CountDown/index.tsx、apps/ui-tars/src/renderer/src/components/Detail/NavHeader.tsx、apps/ui-tars/src/renderer/src/pages/home/index.tsx`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`multimodal/agent-tars/cli/rslib.config.ts`

### 🔵 低｜[維護] 未處理 issue 偏多（426 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 3 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`multimodal/tarko/llm/examples/original/function-call/gemini.md（Gemini CLI 指令）、multimodal/websites/docs/docs/en/api/config/agent.md（Agent 指令（AGENT.md））、multimodal/websites/docs/docs/zh/api/config/agent.md（Agent 指令（AGENT.md））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 37 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：桌面／終端控制

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 22 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-05`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.bytedance/mcp-server-browser`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 38708｜fork 3909｜語言 TypeScript｜建立 2025-01-19｜最後推送 2026-08-05

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*