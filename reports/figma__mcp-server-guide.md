# MCP 安檢報告：figma/mcp-server-guide

> **結論：🟢 未發現明顯風險**　常見風險樣式均未命中；仍建議只給最小權限憑證。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `figma/mcp-server-guide` |
| 專案說明 | A guide on how to use the Figma MCP server |
| 星數 / Fork | ⭐ 1827 / 170 |
| 最後更新 | 2026-07-30 |
| 授權 | 無 |
| 已掃描檔案 | 121 個 |
| 檢查時間 | 2026-07-30 22:09 |

## 風險摘要

🟡 中 1　🔵 低 3　⚪ 資訊 7

## 詳細發現

### 🟡 中｜[權限] 會連往 18 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`api.figma.com、developer.mozilla.org、developers.figma.com、en.wikipedia.org、figma.com、help.figma.com、learn.microsoft.com、mcp.figma.com、mynewssite.com、oreillymedia.github.io…`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`workflow-skills/video-interaction-mapper/scripts/extract_key_frames.py、workflow-skills/video-interaction-mapper/scripts/resolve_moment_frames.py`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`workflow-skills/video-interaction-mapper/scripts/extract_key_frames.py、workflow-skills/video-interaction-mapper/scripts/generate_figma_calls.py、workflow-skills/video-interaction-mapper/scripts/prepare_upload_frames.py、workflow-skills/video-interaction-mapper/scripts/resolve_moment_frames.py`

### 🔵 低｜[身分] 沒有授權條款（License）

沒有 LICENSE 檔，法律上你其實沒有被授權使用或散布。

### ⚪ 資訊｜[代理指令檔] 已掃描 14 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`skills/figma-code-connect/SKILL.md（Agent Skill 指令（SKILL.md））、skills/figma-create-new-file/SKILL.md（Agent Skill 指令（SKILL.md））、skills/figma-design-to-code/SKILL.md（Agent Skill 指令（SKILL.md））、skills/figma-generate-design/SKILL.md（Agent Skill 指令（SKILL.md））、skills/figma-generate-diagram/SKILL.md（Agent Skill 指令（SKILL.md））、skills/figma-generate-library/SKILL.md（Agent Skill 指令（SKILL.md））…`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 5 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-30`

### ⚪ 資訊｜[身分] 官方 registry：網域驗證

發布者以 DNS 記錄證明自己擁有這個網域，因此它背後對應到一個真實可追究的組織。這比只驗證 GitHub 帳號強，但**驗證的是身分不是程式碼**。

> 證據：`registry 名稱 com.figma.mcp/mcp`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1827｜fork 170｜語言 Python｜建立 2025-08-05｜最後推送 2026-07-30

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*