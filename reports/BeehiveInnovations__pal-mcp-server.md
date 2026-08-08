# MCP 安檢報告：BeehiveInnovations/pal-mcp-server

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `BeehiveInnovations/pal-mcp-server` |
| 專案說明 | The power of Claude Code / GeminiCLI / CodexCLI + [Gemini / OpenAI / OpenRouter  |
| 星數 / Fork | ⭐ 11713 / 1034 |
| 最後更新 | 2025-12-15 |
| 授權 | Other |
| 已掃描檔案 | 348 個 |
| 檢查時間 | 2026-08-07 21:38 |

## 風險摘要

🟡 中 2　🔵 低 6　⚪ 資訊 6

## 詳細發現

### 🟡 中｜[權限] 會連往 20 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.example.com、api.openai.com、api.x.ai、bootstrap.pypa.io、claude.ai、core.dialx.ai、custom.dialx.ai、custom.openai.com、custom.x.ai、dialx.ai…`

### 🟡 中｜[維護] 約 8 個月沒有更新

更新頻率偏低，導入前先確認它仍相容你的 MCP 客戶端。

> 證據：`最後推送 2025-12-15`

### 🔵 低｜[供應鏈] 有 5 個依賴未鎖定版本

依賴沒有釘死版本，代表未來安裝時拉到的新版可能與你稽核過的內容不同。

> 證據：`mcp>=1.0.0、google-genai>=1.19.0、openai>=1.55.2、pydantic>=2.0.0、python-dotenv>=1.0.0`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「雲端服務串接」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`clink/agents/base.py、communication_simulator_test.py、docker/scripts/healthcheck.py、simulator_tests/base_test.py、simulator_tests/log_utils.py`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「雲端服務串接」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`clink/agents/base.py、communication_simulator_test.py、docker/scripts/healthcheck.py、providers/registries/base.py、run-server.sh`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「雲端服務串接」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`clink/agents/base.py、run-server.sh、simulator_tests/test_analyze_validation.py、simulator_tests/test_codereview_validation.py、simulator_tests/test_debug_validation.py`

### 🔵 低｜[維護] 未處理 issue 偏多（145 則）

可能代表維護者回應不及，遇到問題時求助無門。

### 🔵 低｜[身分] 未登錄官方 MCP registry

這個專案沒有出現在 modelcontextprotocol.io 的官方註冊表中。很多好用的 MCP 都還沒登錄，這本身不是問題；但也代表沒有任何第三方驗證過「發布者是誰」，你得自己確認來源。

### ⚪ 資訊｜[代理指令檔] 已掃描 3 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/commands/fix-github-issue.md（AI 客戶端設定目錄下的指令檔）、AGENTS.md（Agent 指令（AGENTS.md 慣例））、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））`

### ⚪ 資訊｜[供應鏈] PyPI 上查無此套件（pal-mcp-server）

原始碼宣告了套件名但 PyPI 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 167 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：雲端服務串接

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 11713｜fork 1034｜語言 Python｜建立 2025-06-08｜最後推送 2025-12-15

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*