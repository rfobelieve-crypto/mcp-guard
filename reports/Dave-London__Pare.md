# MCP 安檢報告：Dave-London/Pare

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `Dave-London/Pare` |
| 專案說明 | Dev tools, optimized for agents. Structured, token-efficient MCP servers for git |
| 星數 / Fork | ⭐ 138 / 12 |
| 最後更新 | 2026-08-25 |
| 授權 | MIT License |
| npm 套件 | `pare` |
| 已掃描檔案 | 438 個 |
| 檢查時間 | 2026-08-28 05:13 |

## 風險摘要

🟠 高 2　🟡 中 3　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[供應鏈] npm 套件標示的倉庫與實際來源不一致

套件明確指向的 repo 跟我們稽核的這個不是同一個。這可能是改名／monorepo，也可能是仿冒（typosquatting），需人工確認。

> 證據：`npm repository=git+https://github.com/bendrucker/pare.git｜稽核對象=Dave-London/Pare`

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「桌面／終端控制」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`benchmarks/v2/scripts/benchmark-v2-mutating.ts`

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "husky"`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 7 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.example.com、biomejs.dev、glama.ai、httpbin.org、rolldown.rs、static.modelcontextprotocol.io、unpkg.com`

### 🔵 低｜[供應鏈] 有 16 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@changesets/changelog-github@^1.0.0、@changesets/cli@^3.0.0、@modelcontextprotocol/sdk@^1.30.0、@typescript-eslint/eslint-plugin@^8.67.0、@typescript-eslint/parser@^8.67.0、@vitest/coverage-v8@^4.1.10…`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`benchmarks/v2/scripts/benchmark-v2-mutating.ts、benchmarks/v2/scripts/benchmark-v2.ts、benchmarks/v2/scripts/benchmark.ts、packages/init/__tests__/integration.test.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`benchmarks/v2/scripts/benchmark-v2-mutating.ts、benchmarks/v2/scripts/benchmark-v2.ts、packages/init/src/lib/clients.ts、packages/server-build/src/tools/esbuild.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`packages/init/__tests__/realfs.test.ts、packages/init/src/lib/config-writers/json-mcpservers.ts、packages/init/src/lib/config-writers/json-vscode.ts、packages/init/src/lib/config-writers/json-zed.ts、packages/init/src/lib/config-writers/toml-codex.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 6 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`rules/.clinerules/pare.md（AI 客戶端設定目錄下的指令檔）、rules/.cursor/rules/pare.mdc（AI 客戶端設定目錄下的指令檔）、rules/.github/copilot-instructions.md（GitHub Copilot 指令）、rules/.windsurfrules（Windsurf 規則）、rules/CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、rules/GEMINI.md（Gemini CLI 指令）`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 215 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：桌面／終端控制

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 3 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-25`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.Dave-London/docker`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 138｜fork 12｜語言 TypeScript｜建立 2026-02-10｜最後推送 2026-08-25

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*