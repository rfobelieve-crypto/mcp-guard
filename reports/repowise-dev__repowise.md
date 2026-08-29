# MCP 安檢報告：repowise-dev/repowise

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `repowise-dev/repowise` |
| 專案說明 | Codebase intelligence for AI and humans: code health scores, auto-generated docs |
| 星數 / Fork | ⭐ 6262 / 672 |
| 最後更新 | 2026-08-28 |
| 授權 | GNU Affero General Public License v3.0 |
| npm 套件 | `repowise-root`（registry 查無） |
| 已掃描檔案 | 430 個 |
| 檢查時間 | 2026-08-29 03:07 |

## 風險摘要

🟡 中 1　🔵 低 5　⚪ 資訊 8

## 詳細發現

### 🟡 中｜[權限] 會連往 25 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`aistudio.google.com、api.example.dev、api.repowise.dev、app.edenai.run、claude.com、code.visualstudio.com、console.anthropic.com、cursor.com、developers.openai.com、docs.claude.com…`

### 🔵 低｜[供應鏈] 有 27 個依賴未鎖定版本

依賴沒有釘死版本，代表未來安裝時拉到的新版可能與你稽核過的內容不同。

> 證據：`httpx>=0.27,<1、tree-sitter>=0.23,<1、tree-sitter-python>=0.23,<1、tree-sitter-typescript>=0.23,<1、tree-sitter-javascript>=0.23,<1、tree-sitter-go>=0.23,<1…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`docs/design/contrast_check.py、packages/cli/src/repowise/cli/agent_adapters/claude_code.py、packages/cli/src/repowise/cli/agent_targets/targets/codex.py、packages/cli/src/repowise/cli/agent_targets/targets/cursor.py、packages/cli/src/repowise/cli/agent_targets/targets/hermes.py`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`packages/cli/src/repowise/cli/agent_adapters/claude_code.py、packages/cli/src/repowise/cli/agent_targets/targets/hermes.py、packages/cli/src/repowise/cli/agent_targets/targets/opencode.py、packages/cli/src/repowise/cli/commands/augment_cmd/_shared.py、packages/cli/src/repowise/cli/commands/augment_cmd/fast_lookup.py`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`packages/cli/src/repowise/cli/agent_targets/types.py、packages/cli/src/repowise/cli/commands/augment_cmd/bash_staleness.py、packages/cli/src/repowise/cli/commands/augment_cmd/decision_inject.py、packages/cli/src/repowise/cli/commands/augment_cmd/session_start.py、packages/cli/src/repowise/cli/commands/distill_cmd.py`

### 🔵 低｜[維護] 未處理 issue 偏多（189 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 12 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`plugins/claude-code/skills/architectural-decisions/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude-code/skills/change-review/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude-code/skills/code-health/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude-code/skills/codebase-exploration/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude-code/skills/dead-code-cleanup/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/claude-code/skills/pre-modification/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（repowise-root）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 3 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-28`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 dev.repowise/repowise`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 6262｜fork 672｜語言 Python｜建立 2026-03-23｜最後推送 2026-08-28

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*