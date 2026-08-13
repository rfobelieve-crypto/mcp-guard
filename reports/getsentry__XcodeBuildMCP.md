# MCP 安檢報告：getsentry/XcodeBuildMCP

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `getsentry/XcodeBuildMCP` |
| 專案說明 | A Model Context Protocol (MCP) server and CLI that provides tools for agent use  |
| 星數 / Fork | ⭐ 6231 / 314 |
| 最後更新 | 2026-08-12 |
| 授權 | MIT License |
| npm 套件 | `xcodebuildmcp` |
| 已掃描檔案 | 400 個 |
| 檢查時間 | 2026-08-13 21:44 |

## 風險摘要

🟡 中 2　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[供應鏈] 安裝時會自動執行腳本：prepare

npm/pnpm 安裝過程就會執行這段指令——你還沒使用它，程式碼已經跑過一次了。這是供應鏈投毒最常見的落點，務必逐字讀懂它在做什麼。

> 證據：`"prepare": "node scripts/install-git-hooks.js"`

### 🟡 中｜[權限] 會連往 14 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`eslint.org、feross.org、mcp.sentry.dev、nodejs.org、opencollective.com、paulmillr.com、registry.modelcontextprotocol.io、static.modelcontextprotocol.io、tidelift.com、unpkg.com…`

### 🔵 低｜[供應鏈] 有 28 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@clack/prompts@^1.0.1、@modelcontextprotocol/sdk@^1.27.1、@sentry/node@^10.43.0、bplist-parser@^0.3.2、chokidar@^5.0.0、glob@^13.0.6…`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.agents/skills/warden-sweep/scripts/_utils.py、.agents/skills/warden-sweep/scripts/create_issue.py、.agents/skills/warden-sweep/scripts/organize.py、.agents/skills/warden-sweep/scripts/scan.py、.vscode/settings.json`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.agents/skills/warden-sweep/scripts/_utils.py、.agents/skills/warden-sweep/scripts/extract_findings.py、.agents/skills/warden-sweep/scripts/generate_report.py、.agents/skills/warden-sweep/scripts/index_prs.py、.agents/skills/warden-sweep/scripts/organize.py`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/warden-sweep.yml、scripts/probe-xcode-mcpbridge.ts、scripts/warden-watchdog.mjs、src/benchmarks/claude-ui/__tests__/claude-ui-benchmark.test.ts、src/benchmarks/claude-ui/__tests__/preflight-commands.test.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 19 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.agents/skills/warden-sweep/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/warden/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/xcodebuildmcp-docs-command-review/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/xcodebuildmcp-docs-release-review/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/xcodebuildmcp-packaging-resource-review/SKILL.md（Agent Skill 指令（SKILL.md））、.agents/skills/xcodebuildmcp-rendering-streaming-review/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 17 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：桌面／終端控制

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 1 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-12`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 com.xcodebuildmcp/XcodeBuildMCP`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 6231｜fork 314｜語言 TypeScript｜建立 2025-03-09｜最後推送 2026-08-12

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*