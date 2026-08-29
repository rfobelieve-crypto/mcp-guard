# MCP 安檢報告：mock-server/mockserver-monorepo

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `mock-server/mockserver-monorepo` |
| 專案說明 | MockServer is an HTTP(S) mock server and proxy for testing that lets you mock AP |
| 星數 / Fork | ⭐ 4956 / 1115 |
| 最後更新 | 2026-08-29 |
| 授權 | Apache License 2.0 |
| 已掃描檔案 | 536 個 |
| 檢查時間 | 2026-08-29 03:07 |

## 風險摘要

🟡 中 2　🔵 低 2　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[代理指令檔] 指令檔提及金鑰或 SSH 路徑

若這份指令的主題本來就是金鑰管理屬正常；否則要問：一份操作說明為什麼需要讓模型知道私鑰放在哪裡。

> 證據：`.opencode/skills/renew-test-certs/SKILL.md｜「- `authentication/mtls/leaf-key.pem` is **PKCS#1** (`-----BEGIN RSA PRIVATE KEY-----`) and is consumed by `PEMToFileTest` for traditional-RSA encod…」`

### 🟡 中｜[權限] 會連往 16 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.buildkite.com、api.nuget.org、blog.jamesdbloom.com、central.sonatype.com、dl.k8s.io、docs.rs、downloads.mock-server.com、get.helm.sh、maven.apache.org、mock-server.com…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.buildkite/scripts/steps/diff-coverage.sh、.buildkite/scripts/steps/java-collect-failures.sh、.buildkite/scripts/steps/node-client-browser-test.sh、.buildkite/scripts/steps/ui-e2e.sh、.opencode/plugins/buildkite-status.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.opencode/plugins/buildkite-status.ts`

### ⚪ 資訊｜[代理指令檔] 已掃描 59 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`.claude/agents/code-reviewer.md（AI 客戶端設定目錄下的指令檔）、.claude/agents/council-seat.md（AI 客戶端設定目錄下的指令檔）、.claude/agents/debugger.md（AI 客戶端設定目錄下的指令檔）、.claude/agents/docs-writer.md（AI 客戶端設定目錄下的指令檔）、.claude/agents/implementer.md（AI 客戶端設定目錄下的指令檔）、.claude/agents/pipeline-investigator.md（AI 客戶端設定目錄下的指令檔）…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 4 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、PRIVATE_KEY、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-29`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 com.mock-server/mockserver`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 4956｜fork 1115｜語言 Java｜建立 2013-02-26｜最後推送 2026-08-29

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*