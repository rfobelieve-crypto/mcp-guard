# MCP 安檢報告：BetterDB-inc/monitor

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `BetterDB-inc/monitor` |
| 專案說明 | Real-time monitoring, slowlog analysis, and audit trails for Valkey and Redis |
| 星數 / Fork | ⭐ 1248 / 80 |
| 最後更新 | 2026-07-28 |
| 授權 | Other |
| npm 套件 | `betterdb-monitor`（registry 查無） |
| 已掃描檔案 | 443 個 |
| 檢查時間 | 2026-07-28 22:08 |

## 風險摘要

🟡 中 1　🔵 低 4　⚪ 資訊 8

## 詳細發現

### 🟡 中｜[權限] 會連往 17 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`analytics.internal.example.com、api.example.com、betterdb.com、docs.betterdb.com、eu.i.posthog.com、events.pagerduty.example.com、hooks.slack.example.com、json.schemastore.org、ph.example.com、redis.io…`

### 🔵 低｜[供應鏈] 有 5 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`concurrently@^9.2.1、eslint@^10.1.0、prettier@^3.8.1、turbo@^2.9.14、typescript@^5.9.3`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/agent-cache-py-release.yml、.github/workflows/agent-cache-release.yml、.github/workflows/agent-memory-py-release.yml、.github/workflows/agent-memory-release.yml、.github/workflows/mcp-release.yml`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/agent-cache-py-release.yml、.github/workflows/agent-cache-release.yml、.github/workflows/agent-memory-py-release.yml、.github/workflows/agent-memory-release.yml、.github/workflows/agent-release.yml`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`apps/api/scripts/index-docs.ts、apps/api/src/migration/__tests__/migration-execution.service.spec.ts、apps/api/src/migration/execution/execution-job.ts、apps/api/src/migration/migration-execution.service.ts、apps/api/test/global-setup.ts`

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（betterdb-monitor）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 580 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 1 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-28`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.BetterDB-inc/monitor`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1248｜fork 80｜語言 TypeScript｜建立 2025-12-29｜最後推送 2026-07-28

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*