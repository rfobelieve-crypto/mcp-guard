# MCP 安檢報告：bergside/typeui

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `bergside/typeui` |
| 專案說明 | Build better UI with AI |
| 星數 / Fork | ⭐ 1873 / 137 |
| 最後更新 | 2026-07-04 |
| 授權 | Other |
| npm 套件 | `typeui.sh` |
| 已掃描檔案 | 98 個 |
| 檢查時間 | 2026-09-04 22:51 |

## 風險摘要

🟠 高 1　🟡 中 2　🔵 低 3　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「桌面／終端控制」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`src/prompts/designSystem.ts、src/prompts/registry.ts`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 9 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`assets.typeui.sh、bergside.com、fonts.google.com、mcp.typeui.sh、opencode.ai、opencollective.com、static.modelcontextprotocol.io、tidelift.com、www.typeui.sh`

### 🔵 低｜[供應鏈] 有 7 個依賴未鎖定版本

依賴用浮動版號，代表未來自動拉到的新版可能與你稽核過的內容不同。

> 證據：`commander@^14.0.3、inquirer@^12.11.1、zod@^4.3.6、@types/node@^25.3.3、tsx@^4.21.0、typescript@^5.9.3…`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`plugins/hermes/typeui/typeui_hermes/tools.py、src/generation/existingDesignSystem.ts、src/io/updateSkillFile.ts、test/runDesignGeneration.test.ts、test/runPull.test.ts`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「桌面／終端控制」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`plugins/hermes/typeui/typeui_hermes/tools.py`

### ⚪ 資訊｜[代理指令檔] 已掃描 4 個代理指令檔

這些檔案會被 AI 客戶端自動讀進模型上下文，內容等同於一段你不會逐字讀、模型卻完全服從的提示詞。即使本次沒有命中，安裝前也值得親自看過。

> 證據：`plugins/grok/typeui/skills/typeui/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/hermes/typeui/typeui_hermes/skills/typeui/SKILL.md（Agent Skill 指令（SKILL.md））、plugins/openclaw/typeui/skills/typeui/SKILL.md（Agent Skill 指令（SKILL.md））、skills/fundamentals/SKILL.md（Agent Skill 指令（SKILL.md））`

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 12 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：桌面／終端控制

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`PASSWORD、TOKEN`

### ⚪ 資訊｜[維護] 最近 63 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-04`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.bergside/typeui`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 1873｜fork 137｜語言 TypeScript｜建立 2026-03-03｜最後推送 2026-07-04

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*