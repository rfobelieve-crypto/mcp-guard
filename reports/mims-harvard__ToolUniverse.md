# MCP 安檢報告：mims-harvard/ToolUniverse

> **結論：🟡 需人工複核**　發現 4 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `mims-harvard/ToolUniverse` |
| 專案說明 | Democratizing AI scientists with ToolUniverse |
| 星數 / Fork | ⭐ 1601 / 243 |
| 最後更新 | 2026-07-31 |
| 授權 | Apache License 2.0 |
| 已掃描檔案 | 816 個 |
| 檢查時間 | 2026-07-31 22:08 |

## 風險摘要

🟠 高 4　🟡 中 2　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[代理指令檔] 指令檔要求下載並直接執行遠端腳本

叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——你稽核過的原始碼完全管不到它。

> 證據：`plugin/skills/setup-tooluniverse/SKILL.md｜「```bash curl -LsSf https://astral.sh/uv/install.sh | sh ``` (This is a safe, standard command that downloads and installs `uv…」（另 2 個檔案有相同內容）`

### 🟠 高｜[代理指令檔] 指令檔要求下載並直接執行遠端腳本

叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——你稽核過的原始碼完全管不到它。

> 證據：`plugin/skills/tooluniverse-antigravity-plugin/SKILL.md｜「```bash uv --version # provides `uvx`; if missing: curl -LsSf https://astral.sh/uv/install.sh | sh agy --version # Antigravity CLI; if missing: https://antigravity.goo…」（另 1 個檔案有相同內容）`

### 🟠 高｜[代理指令檔] 指令檔要求下載並直接執行遠端腳本

叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——你稽核過的原始碼完全管不到它。

> 證據：`plugin/skills/tooluniverse-claude-code-plugin/SKILL.md｜「```bash uv --version # must exist; if not: curl -LsSf https://astral.sh/uv/install.sh | sh claude --version # Claude Code CLI; if not: https://claude.com/claud…」（另 1 個檔案有相同內容）`

### 🟠 高｜[代理指令檔] 指令檔要求下載並直接執行遠端腳本

叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——你稽核過的原始碼完全管不到它。

> 證據：`plugins/tooluniverse/skills/tooluniverse-codex-plugin/SKILL.md｜「```bash uv --version # provides `uvx`; if missing: curl -LsSf https://astral.sh/uv/install.sh | sh codex --version # OpenAI Codex CLI; if missing: https://developers.o…」（另 1 個檔案有相同內容）`

### 🟡 中｜[代理指令檔] 指令檔要求下載並直接執行遠端腳本（疑為引述或警告）

叫模型把遠端內容直接餵進 shell，執行的是什麼由對方伺服器當下決定——你稽核過的原始碼完全管不到它。

這段文字帶有講解或警告的語氣（被引號包住、或鄰近出現「不要／避免／untrusted」之類的字眼），因此已降級——安全類專案的文件經常引述這些寫法，把防禦方指控成攻擊方是更難挽回的錯誤。請確認它確實是在說明，而不是在指示。

> 證據：`plugin/skills/tooluniverse-claude-code-plugin/SKILL.md｜「…(most common cause of "no tools at all") command -v uvx || echo "FIX: curl -LsSf https://astral.sh/uv/install.sh | sh"」（另 3 個檔案有相同內容）`

### 🟡 中｜[權限] 會連往 37 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`aiscientist.tools、aistudio.google.com、api.example.com、astral.sh、build.nvidia.com、data.4dnucleome.org、data.humancellatlas.org、depmap.org、docs.astral.sh、fonts.googleapis.com…`

### 🔵 低｜[供應鏈] 有 11 個依賴未鎖定版本

依賴沒有釘死版本，代表未來安裝時拉到的新版可能與你稽核過的內容不同。

> 證據：`requests>=2.32.0、numpy>=2.2.0、graphql-core>=3.2.0、fastapi>=0.116.0、uvicorn>=0.36.0、pydantic>=2.11.0…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`examples/agentic_streaming_example.py、examples/azure_openai_models_example.py、examples/benchmark_batch_vs_single.py、examples/cache_stress_test.py、examples/cache_usage_example.py`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`examples/alphafold_tool_example.py、examples/code_executor/direct_demo.py、examples/code_executor/python_executor_example.py、examples/code_executor/simple_dependency_demo.py、examples/compact_mode/stdio_wrapper.py`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`examples/compact_mode/stdio_wrapper.py、examples/compact_mode/test_stdio_simple.py、examples/hooks_direct_example.py、examples/mcp/debug_transport_closed.py、examples/mcp/mcp_server_example.py`

### ⚪ 資訊｜[代理指令檔] 已掃描 433 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`plugin/skills/setup-tooluniverse/SKILL.md（Agent Skill 指令（SKILL.md））、plugin/skills/tooluniverse-acmg-variant-classification/SKILL.md（Agent Skill 指令（SKILL.md））、plugin/skills/tooluniverse-admet-prediction/SKILL.md（Agent Skill 指令（SKILL.md））、plugin/skills/tooluniverse-adverse-event-detection/SKILL.md（Agent Skill 指令（SKILL.md））、plugin/skills/tooluniverse-adverse-outcome-pathway/SKILL.md（Agent Skill 指令（SKILL.md））、plugin/skills/tooluniverse-aging-senescence/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 12 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-31`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.mims-harvard/tooluniverse`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1601｜fork 243｜語言 Python｜建立 2025-03-03｜最後推送 2026-07-31

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*