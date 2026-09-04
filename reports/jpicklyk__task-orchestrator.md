# MCP 安檢報告：jpicklyk/task-orchestrator

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `jpicklyk/task-orchestrator` |
| 專案說明 | Server-enforced workflow discipline for AI agents. An MCP server providing persi |
| 星數 / Fork | ⭐ 206 / 20 |
| 最後更新 | 2026-08-04 |
| 授權 | MIT License |
| 已掃描檔案 | 127 個 |
| 檢查時間 | 2026-09-04 22:54 |

## 風險摘要

🔵 低 3　⚪ 資訊 7

## 詳細發現

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`claude-plugins/task-orchestrator/hooks/config-sync.mjs、claude-plugins/task-orchestrator/hooks/enforce-actor-attribution.mjs、claude-plugins/task-orchestrator/hooks/plan-capture.mjs、claude-plugins/task-orchestrator/hooks/retro-lib.mjs、claude-plugins/task-orchestrator/hooks/session-start.mjs`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`claude-plugins/task-orchestrator/hooks/tests/config-sync.test.mjs、claude-plugins/task-orchestrator/hooks/tests/enforce-actor-attribution.test.mjs、claude-plugins/task-orchestrator/hooks/tests/retro-ack.test.mjs、claude-plugins/task-orchestrator/hooks/tests/retro-backstop.test.mjs、claude-plugins/task-orchestrator/hooks/tests/retro-trigger.test.mjs`

### 🔵 低｜[權限] 會連往 1 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`static.modelcontextprotocol.io`

### ⚪ 資訊｜[代理指令檔] 已掃描 33 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/commands/check_schema_version.md（AI 客戶端設定目錄下的指令檔）、.claude/commands/deploy_to_docker.md（AI 客戶端設定目錄下的指令檔）、.claude/skills/api-compat-review/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/feature-implementation/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/implement/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/implement/WORKTREE.md（AI 客戶端設定目錄下的指令檔）…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 0 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 31 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-04`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.jpicklyk/task-orchestrator`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 206｜fork 20｜語言 Kotlin｜建立 2025-05-22｜最後推送 2026-08-04

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*