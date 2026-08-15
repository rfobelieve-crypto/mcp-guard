# MCP 安檢報告：svnscha/mcp-windbg

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `svnscha/mcp-windbg` |
| 專案說明 | Model Context Protocol for WinDbg. |
| 星數 / Fork | ⭐ 1520 / 147 |
| 最後更新 | 2026-07-20 |
| 授權 | MIT License |
| 已掃描檔案 | 91 個 |
| 檢查時間 | 2026-08-15 21:23 |

## 風險摘要

🟠 高 2　🟡 中 1　🔵 低 2　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 會讀寫本機檔案（超出宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。但它自述是「第三方 API 串接」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`scripts/validate-server-schema.py、src/mcp_windbg/cdb_session.py、src/mcp_windbg/debug_session.py、src/mcp_windbg/tests/e2e/harness.py、src/mcp_windbg/tests/e2e/runner.py`

### 🟠 高｜[權限] ⚠ 會執行外部指令 / 開子行程（超出宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。但它自述是「第三方 API 串接」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`src/mcp_windbg/debug_session.py、src/mcp_windbg/tests/e2e/harness.py、src/mcp_windbg/tests/e2e/runner.py、src/mcp_windbg/tests/test_debug_session.py`

### 🟡 中｜[權限] 會連往 4 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`msdl.microsoft.com、static.modelcontextprotocol.io、svnscha.github.io、unpkg.com`

### 🔵 低｜[供應鏈] 有 4 個依賴未鎖定版本

依賴沒有釘死版本，代表未來安裝時拉到的新版可能與你稽核過的內容不同。

> 證據：`mcp>=1.28.1、pydantic>=2.13.4、starlette>=1.3.1、uvicorn>=0.51.0`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「第三方 API 串接」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`src/mcp_windbg/server.py、src/mcp_windbg/tests/e2e/harness.py、src/mcp_windbg/tests/e2e/runner.py`

### ⚪ 資訊｜[代理指令檔] 已掃描 7 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/rules/documentation.md（AI 客戶端設定目錄下的指令檔）、.claude/rules/markdown.md（AI 客戶端設定目錄下的指令檔）、.github/prompts/dump-triage.prompt.md（GitHub Copilot 提示檔）、CLAUDE.md（Claude Code 專案指令（CLAUDE.md））、src/mcp_windbg/prompts/dump-triage.prompt.md（GitHub Copilot 提示檔）、src/mcp_windbg/prompts/kernel-triage.prompt.md（GitHub Copilot 提示檔）…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 26 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：第三方 API 串接

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 27 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-20`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.svnscha/mcp-windbg`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1520｜fork 147｜語言 Python｜建立 2025-05-02｜最後推送 2026-07-20

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*