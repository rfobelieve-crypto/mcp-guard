# MCP 安檢報告：CursorTouch/Windows-MCP

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `CursorTouch/Windows-MCP` |
| 專案說明 | MCP Server for Computer Use in Windows |
| 星數 / Fork | ⭐ 6510 / 793 |
| 最後更新 | 2026-07-24 |
| 授權 | MIT License |
| 已掃描檔案 | 108 個 |
| 檢查時間 | 2026-07-27 19:24 |

## 風險摘要

🟡 中 1　🔵 低 4　⚪ 資訊 4

## 詳細發現

### 🟡 中｜[權限] 會連往 9 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`composio.dev、cursortouch.com、docs.github.com、docs.microsoft.com、learn.microsoft.com、my-client.example.com、static.modelcontextprotocol.io、us.i.posthog.com、youtu.be`

### 🔵 低｜[工具描述投毒] 描述含「優先呼叫本工具」的措辭

這在正常 MCP 中很常見（引導模型選對工具），但也是投毒用來搶奪呼叫權的手法。請確認它引導的方向合理、且沒有附帶額外指令。

> 證據：`src/windows_mcp/tools/snapshot.py｜「Take a screenshot and inspect the screen. Keywords: screenshot, screen capture, see screen, observe, look, inspect, UI e」`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`src/windows_mcp/__main__.py、src/windows_mcp/powershell/service.py、src/windows_mcp/powershell/utils.py、src/windows_mcp/tools/app.py、tests/test_app_tool.py`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`src/windows_mcp/__main__.py、src/windows_mcp/config.py、src/windows_mcp/desktop/flash_overlay.py、src/windows_mcp/desktop/screenshot.py、src/windows_mcp/desktop/service.py`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`src/windows_mcp/filesystem/service.py、src/windows_mcp/powershell/service.py、src/windows_mcp/powershell/utils.py、src/windows_mcp/tools/app.py、tests/test_analytics.py`

### ⚪ 資訊｜[權限] 判定用途：桌面／終端控制

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 3 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-24`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 6510｜fork 793｜語言 Python｜建立 2025-05-13｜最後推送 2026-07-24

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*