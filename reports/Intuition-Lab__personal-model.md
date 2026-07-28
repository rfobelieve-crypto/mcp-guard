# MCP 安檢報告：Intuition-Lab/personal-model

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `Intuition-Lab/personal-model` |
| 專案說明 | Build your HUMAN.md. |
| 星數 / Fork | ⭐ 1237 / 97 |
| 最後更新 | 2026-07-28 |
| 授權 | Apache License 2.0 |
| 已掃描檔案 | 400 個 |
| 檢查時間 | 2026-07-28 15:03 |

## 風險摘要

🟠 高 1　🟡 中 1　🔵 低 5　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[身分] 倉庫非常新（建立於 18 天前）

新建立的 repo 本身不等於惡意，但若它同時被大量宣傳、或使用了熱門既有名稱，要特別留意是否為搶註／仿冒。

> 證據：`2026-07-10`

### 🟡 中｜[權限] 會連往 33 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.anthropic.com、api.cerebras.ai、api.deepseek.com、api.example、api.fireworks.ai、api.groq.com、api.mistral.ai、api.moonshot.ai、api.moonshot.cn、api.openai.com…`

### 🔵 低｜[供應鏈] 有 10 個依賴未鎖定版本

依賴沒有釘死版本，代表未來安裝時拉到的新版可能與你稽核過的內容不同。

> 證據：`typer>=0.12、rich>=13.7、python-frontmatter>=1.1、mss>=9.0、Pillow>=10.0、mcp>=1.23.0…`

### 🔵 低｜[工具描述投毒] 描述含「優先呼叫本工具」的措辭

這在正常 MCP 中很常見（引導模型選對工具），但也是投毒用來搶奪呼叫權的手法。請確認它引導的方向合理、且沒有附帶額外指令。

> 證據：`src/persome/mcp/server.py｜「**ALWAYS CALL FIRST** on the first personal-context turn of a conversation.

        List all memory files with descript」`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/release.yml、clients/persome-companion/Bridge/cli.js、clients/persome-companion/Bridge/server.js、clients/persome-companion/Bridge/store.js、install.sh`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`clients/persome-companion/Bridge/cli.js、scripts/build_pypi_dist.py、src/persome/capture/ax_capture.py、src/persome/capture/browser_detect.py、src/persome/capture/ocr_health.py`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`clients/persome-companion/Bridge/cli.js、pyi_entrypoint.py、pyi_rthook_ssl.py、scripts/pii_scan.py、scripts/probe_prompt_cache.py`

### ⚪ 資訊｜[代理指令檔] 已掃描 2 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））`

### ⚪ 資訊｜[供應鏈] PyPI 上查無此套件（persome-core）

原始碼宣告了套件名但 PyPI 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-28`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.Intuition-Lab/personal-model`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1237｜fork 97｜語言 Python｜建立 2026-07-10｜最後推送 2026-07-28

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*