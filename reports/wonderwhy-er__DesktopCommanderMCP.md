# MCP 安檢報告：wonderwhy-er/DesktopCommanderMCP

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `wonderwhy-er/DesktopCommanderMCP` |
| 專案說明 | This is MCP server for Claude that gives it terminal control, file system search |
| 星數 / Fork | ⭐ 8980 / 1029 |
| 最後更新 | 2026-07-30 |
| 授權 | MIT License |
| npm 套件 | `@wonderwhy-er/desktop-commander` |
| 已掃描檔案 | 269 個 |
| 檢查時間 | 2026-07-30 22:04 |

## 風險摘要

🟠 高 1　🟡 中 2　🔵 低 5　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[供應鏈] 安裝時會自動執行腳本：postinstall

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"postinstall": "node dist/track-installation.js && node dist/npm-scripts/verify-ripgrep.js || node -e "process.exit(0)""`

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "npm run build"`

### 🟡 中｜[權限] 會連往 22 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`avatars.githubusercontent.com、calendar.app.google、claude.ai、dc-telemetry-proxy-83847352264.europe-west1.run.app、desktopcommander.app、discord.com、docs.docker.com、legal.desktopcommander.app、list.agenium.net、mcp.desktopcommander.app…`

### 🔵 低｜[供應鏈] 有 46 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@modelcontextprotocol/sdk@^1.9.0、@opendocsg/pdf2md@^0.2.2、@supabase/supabase-js@^2.89.0、@tiptap/core@^3.22.3、@tiptap/extension-image@^3.22.3、@tiptap/extension-table@^3.22.4…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`install-docker.sh、scripts/build-mcpb.cjs、scripts/build-ui-runtime.cjs、scripts/download-all-ripgrep.cjs、scripts/export-fuzzy-logs.js`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`scripts/build-mcpb.cjs、scripts/count-tokens.js、scripts/download-all-ripgrep.cjs、scripts/publish-release.cjs、scripts/validate-tools-sync.js`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`scripts/count-tokens.js、scripts/publish-release.cjs、scripts/ripgrep-wrapper.js、setup-claude-server.js、src/bootstrap.ts`

### 🔵 低｜[維護] 未處理 issue 偏多（195 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 20 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`plugins/claude/skills/ai-tools-setup/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude/skills/computer-health-check/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude/skills/desktop-commander-overview/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude/skills/knowledge-base/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude/skills/obsidian-vault/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude/skills/terminal/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 38 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：桌面／終端控制

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 1 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-30`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.wonderwhy-er/desktop-commander`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 8980｜fork 1029｜語言 TypeScript｜建立 2024-12-04｜最後推送 2026-07-30

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*