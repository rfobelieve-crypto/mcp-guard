# MCP 安檢報告：dongdongbh/Mindwtr

> **結論：🟡 需人工複核**　發現 2 項高風險項目，請逐項讀懂後再決定。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `dongdongbh/Mindwtr` |
| 專案說明 | Get every task and idea out of your head, then see the next thing to do. Getting |
| 星數 / Fork | ⭐ 1656 / 96 |
| 最後更新 | 2026-08-12 |
| 授權 | GNU Affero General Public License v3.0 |
| npm 套件 | `mindwtr-monorepo`（registry 查無） |
| 已掃描檔案 | 410 個 |
| 檢查時間 | 2026-08-12 21:46 |

## 風險摘要

🟠 高 2　🟡 中 1　🔵 低 3　⚪ 資訊 8

## 詳細發現

### 🟠 高｜[權限] ⚠ 會讀寫本機檔案（超出宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。但它自述是「第三方 API 串接」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`.github/workflows/ci.yml、.github/workflows/publish-mcp.yml、.github/workflows/release-android.yml、.github/workflows/release-linux.yml、.github/workflows/release-macos-appstore.yml`

### 🟠 高｜[權限] ⚠ 會執行外部指令 / 開子行程（超出宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。但它自述是「第三方 API 串接」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`apps/cloud/src/server.test.ts`

### 🟡 中｜[權限] 會連往 31 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`ai.example.com、aka.ms、androidpublisher.googleapis.com、api.appstoreconnect.apple.com、archive.ubuntu.com、asset.localhost、aur.archlinux.org、azure.archive.ubuntu.com、calendar.example、cloud.example…`

### 🔵 低｜[供應鏈] 有 63 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`@babel/runtime@^7.28.4、@radix-ui/react-compose-refs@^1.1.2、@radix-ui/react-slot@^1.2.4、@react-native/assets-registry@^0.82.1、@react-native/normalize-colors@^0.82.1、@react-native/virtualized-lists@^0.82.1…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「第三方 API 串接」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/release-macos-appstore.yml、.github/workflows/release-macos.yml、.github/workflows/release-rc.yml、.github/workflows/release.yml、.github/workflows/update-aur-beta.yml`

### 🔵 低｜[維護] 未處理 issue 偏多（67 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[供應鏈] npm 上查無此套件（mindwtr-monorepo）

原始碼宣告了套件名但 registry 查不到，代表尚未發佈或用其他方式散布。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 4 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：第三方 API 串接

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-12`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.dongdongbh/mindwtr`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1656｜fork 96｜語言 TypeScript｜建立 2025-12-08｜最後推送 2026-08-12

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*