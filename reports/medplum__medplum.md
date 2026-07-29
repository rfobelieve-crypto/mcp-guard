# MCP 安檢報告：medplum/medplum

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `medplum/medplum` |
| 專案說明 | Medplum is a healthcare platform that helps you quickly develop high-quality com |
| 星數 / Fork | ⭐ 2556 / 871 |
| 最後更新 | 2026-07-29 |
| 授權 | Apache License 2.0 |
| npm 套件 | `root` |
| 已掃描檔案 | 441 個 |
| 檢查時間 | 2026-07-29 22:04 |

## 風險摘要

🟠 高 1　🟡 中 1　🔵 低 3　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[供應鏈] npm 套件標示的倉庫與實際來源不一致

套件明確指向的 repo 跟我們稽核的這個不是同一個。這可能是改名／monorepo，也可能是仿冒（typosquatting），需人工確認。

> 證據：`npm repository=git://github.com/mafintosh/root.git｜稽核對象=medplum/medplum`

### 🟡 中｜[權限] 會連往 81 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`ama-assn.org、api-staging.joincandidhealth.com、api.dev.tryvital.io、api.example.com、api.gethealthie.com、api.healthie.com、api.medplum.com、api.metriport.com、api.opkit.co、api.zoom.us…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/build.yml、.github/workflows/publish.yml、examples/medplum-demo-bots/src/lab-integration/send-orm-message.test.ts、examples/medplum-healthie-importer/src/healthie/integration.test.ts、examples/medplum-healthie-importer/src/healthie/patient.test.ts`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「開發框架／工具鏈」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/publish.yml、examples/medplum-eligibility-demo/src/pages/SearchPage.tsx、examples/medplum-eligibility-demo/src/scripts/deploy-bots.ts`

### 🔵 低｜[維護] 未處理 issue 偏多（607 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 1 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`packages/docs/src/pages/solutions/agent.md（Agent 指令（AGENT.md））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 0 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：開發框架／工具鏈

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-29`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 com.medplum/mcp`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 2556｜fork 871｜語言 TypeScript｜建立 2021-04-21｜最後推送 2026-07-29

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*