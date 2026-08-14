# MCP 安檢報告：mbailey/voicemode

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `mbailey/voicemode` |
| 專案說明 | Natural voice conversations with Claude Code |
| 星數 / Fork | ⭐ 1324 / 183 |
| 最後更新 | 2026-08-09 |
| 授權 | MIT License |
| 已掃描檔案 | 400 個 |
| 檢查時間 | 2026-08-14 21:28 |

## 風險摘要

🟠 高 1　🟡 中 1　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[代理指令檔] 指令檔要求下載並直接執行遠端腳本

叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——你稽核過的原始碼完全管不到它。

> 證據：`.claude/commands/install.md｜「…install process assumes: - **UV** - Python package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`) - **Homebrew** - macOS package manager (install: `brew.sh`)」`

### 🟡 中｜[權限] 會連往 37 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`a.example、api.anthropic.com、api.cartesia.ai、api.example.com、api.openai.com、astral.sh、b.example、brew.sh、cartesia.ai、custom.cloud.service…`

### 🔵 低｜[供應鏈] 有 11 個依賴未鎖定版本

依賴沒有釘死版本，代表未來安裝時拉到的新版可能與你稽核過的內容不同。

> 證據：`uv>=0.4.0、numpy、sounddevice、scipy、pydub、simpleaudio…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`docs/gen_pages.py、installer/voicemode_install/checker.py、installer/voicemode_install/cli.py、installer/voicemode_install/logger.py、installer/voicemode_install/system.py`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`installer/voicemode_install/checker.py、installer/voicemode_install/cli.py、installer/voicemode_install/installer.py、scripts/diagnose-wsl-audio.py、scripts/release.py`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`installer/voicemode_install/cli.py、scripts/conversation_browser.py、scripts/diagnose-wsl-audio.py、scripts/release.py、scripts/test-stt-direct.py`

### ⚪ 資訊｜[代理指令檔] 已掃描 15 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/commands/converse.md（AI 客戶端設定目錄下的指令檔）、.claude/commands/install.md（AI 客戶端設定目錄下的指令檔）、.claude/commands/status.md（AI 客戶端設定目錄下的指令檔）、.claude/skills/converse/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/impressions/SKILL.md（Agent Skill 指令（SKILL.md））、.claude/skills/impressions/docs/finding-samples.md（AI 客戶端設定目錄下的指令檔）…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 4 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 5 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-09`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 dev.voicemode/voicemode`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1324｜fork 183｜語言 Python｜建立 2025-06-08｜最後推送 2026-08-09

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*