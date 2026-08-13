# MCP 安檢報告：MervinPraison/PraisonAI

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `MervinPraison/PraisonAI` |
| 專案說明 | PraisonAI 🦞 — Hire a 24/7 AI Workforce. Stop writing boilerplate and start shipp |
| 星數 / Fork | ⭐ 8831 / 1382 |
| 最後更新 | 2026-08-11 |
| 授權 | MIT License |
| 已掃描檔案 | 433 個 |
| 檢查時間 | 2026-08-12 21:44 |

## 風險摘要

🟠 高 2　🟡 中 3　🔵 低 4　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[供應鏈] setup.py 覆寫了安裝期指令

它以自訂類別接管 install／develop 步驟，等同 npm 的 postinstall：你還沒開始用，程式碼已經跑過一次了。

> 證據：`src/praisonai/praisonai/setup.py:6｜class PostInstallCommand(install)`

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「開發框架／工具鏈」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`examples/js/tools/basic-tools.ts、examples/js/tools/custom-tool.ts、examples/python/agents/math-agent.py`

### 🟡 中｜[供應鏈] setup.py 會在安裝時執行外部指令

常見的正當用途是呼叫 git 取版本號或編譯原生模組；但這確實是安裝當下就會執行的程式碼，值得逐行讀懂。

> 證據：`src/praisonai-code/praisonai_code/cli/commands/setup.py:125｜subprocess（另 1 個 setup.py 相同）`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 26 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`accounts.google.com、api.cloudflare.com、api.example.com、api.groq.com、api.openai.com、astral.sh、auth.example.com、blog.google、cockroachlabs.cloud、docs.docker.com…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/praisonai-issue-triage.yaml、.github/scripts/release-gate.js、.github/workflows/pypi-release.yml、examples/agent_tools/agent_centric_example.py、examples/benchmark/benchmark_example.py`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/scripts/pr-review-chain-selftest.js、.github/scripts/pr-review-chain.js、.github/workflows/auto-pr-comment.yml、.github/workflows/bot-pr-recovery.yml、.github/workflows/ci-failure-claude.yml`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/scripts/release-gate.js、examples/catalog/run_all_catalog_examples.py、examples/doctor/ci_integration.py、examples/endpoints_example.py、examples/js/run-feature-tests.ts`

### 🔵 低｜[維護] 未處理 issue 偏多（108 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 9 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`AGENTS.md（Agent 指令（AGENTS.md 慣例））、examples/skills/pdf-processing/SKILL.md（Agent Skill 指令（SKILL.md））、src/praisonai-agents/.cursorrules（Cursor 規則）、src/praisonai-agents/AGENTS.md（Agent 指令（AGENTS.md 慣例））、src/praisonai-agents/tests/.windsurfrules（Windsurf 規則）、src/praisonai-rust/AGENTS.md（Agent 指令（AGENTS.md 慣例））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 25 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 1 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-11`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.MervinPraison/praisonai`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 8831｜fork 1382｜語言 Python｜建立 2024-03-19｜最後推送 2026-08-11

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*