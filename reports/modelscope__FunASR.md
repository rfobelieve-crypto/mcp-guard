# MCP 安檢報告：modelscope/FunASR

> **結論：🟡 需人工複核**　有 1 項高風險項目，確認它是功能必需後才安裝。

| 項目 | 內容 |
|---|---|
| 稽核對象 | `modelscope/FunASR` |
| 專案說明 | Open-source speech recognition toolkit for training, inference, streaming ASR, V |
| 星數 / Fork | ⭐ 19548 / 1963 |
| 最後更新 | 2026-07-29 |
| 授權 | MIT License |
| 已掃描檔案 | 412 個 |
| 檢查時間 | 2026-07-29 22:02 |

## 風險摘要

🟠 高 1　🟡 中 2　🔵 低 3　⚪ 資訊 7

## 詳細發現

### 🟠 高｜[權限] ⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）

動態執行字串會讓靜態稽核失效，需確認來源不可被外部輸入操控。但它自述是「程式碼／版控工具」，這類用途通常**不需要**這個能力。請確認這是必要功能，而不是多餘或被夾帶的權限。

> 證據：`examples/industrial_data_pretraining/fun_asr_nano/demo2.py、examples/industrial_data_pretraining/fun_asr_nano/model.py`

### 🟡 中｜[權限] 使用動態執行（eval）需額外留意

eval 會讓靜態稽核失效——原始碼看起來安全，執行的內容卻可能來自外部輸入。請確認被執行的字串不可被使用者或遠端資料操控。

### 🟡 中｜[權限] 會連往 18 個外部主機

確認這些連線是功能必需的，而不是把你的資料送到第三方。

> 證據：`ghcr.io、glama.ai、huggingface.co、isv-data.oss-cn-hangzhou.aliyuncs.com、modelscope.cn、modelscope.github.io、modelscope.oss-cn-beijing.aliyuncs.com、opensource.org、qianwen-res.oss-cn-beijing.aliyuncs.com、registry.modelcontextprotocol.io…`

### 🔵 低｜[權限] 會讀取環境變數（符合宣稱用途）

環境變數常存放 API 金鑰。確認它只讀自己需要的那幾個。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`.github/workflows/publish-mcp-server.yml、examples/industrial_data_pretraining/fun_asr_nano/model.py、examples/mcp_server/funasr_mcp.py、examples/mcp_server/test_funasr_mcp.py、examples/openai_api/gradio_app.py`

### 🔵 低｜[權限] 會讀寫本機檔案（符合宣稱用途）

確認它存取的路徑範圍，避免它能讀到憑證、金鑰或私人文件。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`benchmark_vllm.py、examples/aishell/e_paraformer/utils/compute_wer.py、examples/aishell/e_paraformer/utils/extract_embeds.py、examples/aishell/e_paraformer/utils/postprocess_text_zh.py、examples/aishell/e_paraformer/utils/text2token.py`

### 🔵 低｜[權限] 會執行外部指令 / 開子行程（符合宣稱用途）

這個 MCP 能在你的電腦上執行系統指令。「程式碼／版控工具」類工具本來就需要這個能力，屬預期範圍；重點是你**知情**並給予對應的信任。

> 證據：`examples/mcp_server/smoke_test.py、examples/mcp_server/test_funasr_mcp.py、examples/voice_input/funasr_input.py`

### ⚪ 資訊｜[代理指令檔] 沒有代理指令檔

這個專案沒有 SKILL.md／AGENTS.md／CLAUDE.md／.cursorrules 之類會被 AI 客戶端自動讀進上下文的指令檔，因此不存在這個攻擊面。

### ⚪ 資訊｜[工具描述投毒] 未發現可疑工具描述（已掃描 4 段 description）

沒有偵測到已知的注入樣式與隱藏字元。這不等於絕對安全，但常見的 tool poisoning 手法都沒有命中。

### ⚪ 資訊｜[權限] 判定用途：程式碼／版控工具

以下權限均以此用途為基準判斷是否合理。這類工具預期會用到：讀取環境變數、執行外部指令、讀寫本機檔案、連線外部主機。

### ⚪ 資訊｜[權限] 需要的憑證類設定

安裝前先確認這些金鑰的權限範圍，盡量給最小權限、可隨時撤銷的憑證。

> 證據：`API_KEY、PASSWORD、SECRET、TOKEN`

### ⚪ 資訊｜[維護] 最近 0 天內有更新

專案仍在活躍維護中。

> 證據：`最後推送 2026-07-29`

### ⚪ 資訊｜[身分] 官方 registry：GitHub 帳號驗證

發布者只證明了自己擁有那個 GitHub 帳號——任何人都能註冊帳號並登錄。這不是負面訊號，但它提供的保證僅止於「有個帳號」。

> 證據：`registry 名稱 io.github.modelscope/funasr-mcp`

### ⚪ 資訊｜[身分] 倉庫基本資料

⭐ 19548｜fork 1963｜語言 Python｜建立 2022-11-24｜最後推送 2026-07-29

---

## 這份報告不保證什麼

- 這是**靜態稽核**：只讀原始碼與公開中繼資料，**不執行**目標程式，
  因此無法涵蓋僅在執行期才出現的行為（動態下載、遠端下發指令等）。
- 「未發現明顯風險」代表已知樣式沒有命中，**不等於安全背書**。
- 遠端型（hosted）MCP 的實際行為在對方伺服器上，原始碼不代表線上版本。
- 安裝任何 MCP 前，請只給**最小權限、可撤銷**的憑證。

*由 MCP 安檢（mcp-guard）產生 · 繁體中文*