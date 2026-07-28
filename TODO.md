# TODO

> 跨 session 的任務真相源。每次開工先讀這裡的「重啟後立刻要做」。

---

## ⚡ 重啟後立刻要做（GetLayers 接續）

**現況**：GetLayers MCP 已裝好（2026-07-28），但**尚未驗證、尚未生效**。

```
getlayers -> https://mcp.getlayers.ai/mcp (HTTP)
寫入 C:\Users\rfo\.claude.json（user scope，所有專案可用）
狀態：! Needs authentication
```

### 1. 驗證授權（使用者自己做）
```
/mcp          →  選 getlayers 授權
```
⚠️ 前提：官網寫明需要 **Full Stack Lifetime 訂閱**，沒有的話授權過了工具也調不動。

### 2. 補裝 skill（使用者自己做，`/plugin` 是內建指令，Claude 跑不了）
```
/plugin marketplace add textura-agency/getlayers-plugin
/plugin install getlayers@getlayers
```
**為什麼需要**：只裝 MCP 伺服器的話沒有操作流程指南，容易做出「通用輸出」而非真的用到
它的素材庫。skill 的關鍵規則（已讀過 SKILL.md，摘要備查）：
- 一定先呼叫 `getlayers_start`，再用自己的話介紹五種能力
- 五種模式：從零建站 / 3D 場景 / 拉素材 / 影片背景 / 為現有專案加動態
- **不要 strict-filter**：用 `getlayers_search` 以自然語言找，讀描述判斷合適度
- **一定要用 compositions 當版面骨架**，不要通用置中堆疊（最常見的失敗）
- **只定一個 Style**，把 `styleId` 傳給每次 `getlayers_materialize`
- 場景調色透過 **CONFIG 的 tint**，不要改 shader
- 建議環境：`textura-agency/next16-claude-starter`（clone 後移除 .git 重新 init）

### 3. 接上後要做的事
用 GetLayers 重做 mcp-guard 網站，**與現有手寫版並列比較**：
- 現有版：`site.py` 產生，手寫 Canvas 首屏（封包→篩選環→分流）
- 比較點：素材庫品質、3D 場景、動態編排，是否真的優於手寫
- 目標是判斷「那支 IG reel 的質感差距」到底來自素材還是工藝

---

## 產品待辦

### 高優先
- [ ] **把 `SKILL.md` / `AGENTS.md` / `CLAUDE.md` 納入投毒掃描**
      ← 2026-07-28 dogfooding 掃 getlayers-plugin 時發現的自家漏洞。
      這類檔案是「會被載入 AI 上下文的指令」，跟 tool description 同屬攻擊面，
      甚至更直接。當時是手動 grep 才確認乾淨的。
- [ ] **把第一篇文章發到中文社群**（Threads / 方格子 / 知乎 / FB 社團）
      ← 目前最大瓶頸是分發不是功能：站已上線但 ⭐ 0、沒人知道它存在。
      素材現成：`docs/01-一個不存在的MCP.md`
- [ ] **OG 分享圖** — 目前貼連結沒有預覽圖，直接影響社群點擊率。
      這是靜態素材、不需反映資料，適合用 Higgsfield 生成。

### 中優先
- [ ] **沙箱實跑**：在隔離環境啟動 server、`list_tools` 比對「宣告的工具」vs
      「實際暴露的工具」。這是靜態掃描給不了、也是各家 MCP 廣場做不到的護城河。
- [ ] **自訂顯示字體**：標題用開源英文顯示字（子集化幾十 KB），中文維持系統字。
      繁中字型檔 5–10MB 無法整包載入，這是目前與 premium 網站最明顯的差距之一。
- [ ] **WebGL 3D 首屏**：把現有 2D 封包場改成有景深、滑鼠影響視角的 3D 場景。
- [ ] **PyPI 生態支援**：供應鏈檢查目前以 npm 為主。

### 低優先
- [ ] 已知惡意／搶註名稱清單
- [ ] 讓 `batch.py` 的掃描名單可從官方 registry 自動同步

---

## 已完成（2026-07-27 ～ 07-28）

- ✅ 掃描引擎五項檢查（身分／供應鏈／權限／工具描述投毒／維護）
- ✅ 用途推斷分級：區分「本份權限」vs「⚠ 超出宣稱用途」
      （修正前 18 個專案有 15 個是同一個「會開子行程」，毫無區辨度）
- ✅ 紅隊測試 11/11，含 **6 個真實誤報回歸樣本**
      （開發期間對 5 個知名專案誤報 6 次，全部在公開前攔下）
- ✅ 批次掃描 18 個熱門 MCP + 結構化 `data.json`
- ✅ `pip install .` → `mcp-guard` 指令，零第三方相依
- ✅ 第一篇文章〈一個被瘋傳的 MCP，其實不存在〉
- ✅ README 更正政策（公開指名真實專案的前提）
- ✅ GitHub Actions 每日 05:00 重掃 → 部署 Pages（紅隊測試沒過即中止）
- ✅ 網站上線 https://rfobelieve-crypto.github.io/mcp-guard/

---

## 重要決策紀錄

**為什麼不做「又一個 MCP 目錄」**：中文圈已有 8+ 個 MCP 廣場（魔搭約 1500 個
服務、百度／阿里雲百煉／騰訊雲／訊飛星辰），背後是雲端大廠的流量入口，正面對打
沒有勝算。切入點是廣場**結構性做不到**的事：平台不會公告自己上架的東西有毒。

**為什麼首屏動畫手寫而非生成**：它必須逐一評估封包並依真實比例分流——生成的
影片是固定畫面且動輒數 MB。生成工具的正確用途是 OG 圖那種靜態素材。

**為什麼總表不套電影感動態**：那會傷害掃讀效率，而且對信任型產品，過度炫技
反而扣信譽分（參考 Have I Been Pwned / Snyk / Socket.dev 都刻意樸素）。
