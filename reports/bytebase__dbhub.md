# MCP 安檢報告：bytebase/dbhub

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `bytebase/dbhub` |
| 專案說明 | Token conscious database MCP server for Postgres, MySQL, SQL Server, MariaDB, SQ |
| 星數 / Fork | ⭐ 3352 / 288 |
| 最後更新 | 2026-08-08 |
| 授權 | MIT License |
| npm 套件 | `dbhub` |
| 已掃描檔案 | 241 個 |
| 檢查時間 | 2026-08-13 21:46 |

## 風險摘要

🟠 高 1　🟡 中 2　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 會執行外部指令 / 開子行程（超出宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。但它自述是「資料庫存取」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`scripts/build-mcpb.mjs、scripts/smoke-test-mcpb.mjs、src/__tests__/http-bind-host.integration.test.ts、src/__tests__/json-rpc-integration.test.ts`

### 🟡 中｜[代理指令檔] 指令檔提及金鑰或 SSH 路徑

若這份指令的主題本來就是金鑰管理屬正常；否則要問：一份操作說明為什麼需要讓模型知道私鑰放在哪裡。

> 證據：`CLAUDE.md｜「…SH_PASSPHRASE` - SSH config file support: Automatically reads from `~/.ssh/config` when using host aliases - Implementation in `src/utils/ssh-tun…」`

### 🟡 中｜[權限] 會連往 14 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`app.internal、coss.com、database.windows.net、dbhub.ai、evil.attacker.test、evil.com、mintlify.com、registry.modelcontextprotocol.io、static.modelcontextprotocol.io、ui.shadcn.com…`

### 🔵 低｜[供應鏈] 有 29 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@iarna/toml@^2.2.5、@modelcontextprotocol/node@^2.0.0、@modelcontextprotocol/server@^2.0.0、dotenv@^16.4.7、express@^4.18.2、ssh-config@^5.0.3…`

### 🔵 低｜[供應鏈] npm 套件未標示原始碼位置

套件沒有填 repository 欄位，因此**無法自動核對**它是否真的由這個 repo 建置。這不代表有問題，但也代表少了一道可驗證性；安裝前建議自行確認發布者身分。

> 證據：`npm: dbhub（repository 欄位空白）`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「資料庫存取」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`scripts/mcpb-common.mjs、scripts/smoke-test-mcpb.mjs、src/__tests__/http-bind-host.integration.test.ts、src/__tests__/json-rpc-integration.test.ts、src/config/__tests__/env.test.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「資料庫存取」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`scripts/sync-version.mjs、src/__tests__/http-bind-host.integration.test.ts、src/__tests__/json-rpc-integration.test.ts、src/__tests__/plugin-consistency.test.ts、src/config/__tests__/env.test.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 7 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/skills/fix-bug/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/testing/SKILL.md（Agent Skill 指令（SKILL.md））、.github/copilot-instructions.md（GitHub Copilot 指令）、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、plugin/skills/explore/SKILL.md（Agent Skill 指令（SKILL.md））、plugin/skills/setup/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 8 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：資料庫存取

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 5 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-08`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.bytebase/dbhub`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 3352｜fork 288｜語言 TypeScript｜建立 2025-03-09｜最後推送 2026-08-08

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*