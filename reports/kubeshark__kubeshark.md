# MCP 安檢報告：kubeshark/kubeshark

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `kubeshark/kubeshark` |
| 專案說明 | eBPF-powered network observability for Kubernetes. Indexes L4/L7 traffic with fu |
| 星數 / Fork | ⭐ 12057 / 546 |
| 最後更新 | 2026-08-18 |
| 授權 | Apache License 2.0 |
| 已掃描檔案 | 141 個 |
| 檢查時間 | 2026-08-24 21:28 |

## 風險摘要

🟡 中 1　🔵 低 1　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[權限] 會連往 11 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`acme-v02.api.letsencrypt.org、api.kubeshark.com、charts.jetstack.io、docs.github.com、gh.io、golang.org、helm.kubeshark.com、kubeshark.com、kubeshark.example.com、kubeshark.github.io…`

### 🔵 低｜[維護] 未處理 issue 偏多（145 則）

可能代表維護者回應不及，遇到問題時求助無門。

### ⚪ 資訊｜[代理指令檔] 已掃描 4 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`skills/install/SKILL.md（Agent Skill 指令（SKILL.md））、skills/kfl/SKILL.md（Agent Skill 指令（SKILL.md））、skills/network-rca/SKILL.md（Agent Skill 指令（SKILL.md））、skills/security-audit/SKILL.md（Agent Skill 指令（SKILL.md））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 9 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 6 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-08-18`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.kubeshark/mcp`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 12057｜fork 546｜語言 Go｜建立 2021-04-19｜最後推送 2026-08-18

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*