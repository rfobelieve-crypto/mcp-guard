# eval 規則命中測試與範例碼，讓「超出宣稱用途」指向不會安裝的檔案

> 第五篇筆記。與第二、三、四篇同一類：不是外部事件，而是**這個工具自己的判定值得商榷**。
>
> 這一篇的性質接近第四篇——不是「規則寫錯了」，而是**規則的取材範圍**決定了
> 使用者看到的紅字有多少份量。差別在於第四篇談的是「宣稱用途」怎麼來的，
> 這一篇談的是「超出」的證據落在哪裡。
>
> **本文只提出證據與選項，沒有修改 `checks.py`、`fetch.py` 或任何規則。**
> 抓取與評分的範圍是引擎維護者的決定。

---

## 摘要

`eval` 規則本身沒有寫錯。它比對的是

```python
\beval\s*\(|new Function\s*\(|exec\s*\(\s*compile
```

也就是**呼叫**，不是檔名，我在 08-31 那輪特地驗證過這一點。問題不在規則的正確性，
在於它掃的檔案包含了測試、基準、範例——這些**不會隨套件安裝到使用者機器上**的程式碼。

以 2026-09-04 那次重掃（`2da581a`）的資料為準，全庫 178 個專案裡有 **28 筆** eval 類 findings，
每一筆都是 HIGH（標題為「⚠ 使用 eval / 動態執行程式碼（超出宣稱用途）」）。按證據路徑分類：

| 證據路徑 | 筆數 |
|---|---|
| **全部**落在 `tests/`、`__tests__/`、`spec/`、`benchmarks/`、`examples/`、`demos/`、`fixtures/`、`e2e/` | **6** |
| **全部**落在 `scripts/`、`docs/`、`site/`（性質可爭議，見下） | **2** |
| 部分落在上述路徑、部分落在一般程式碼 | 3 |
| 全部落在一般程式碼 | 17 |

前兩列合計 8 筆。**其中 6 個專案除了這一項之外沒有任何其他 HIGH**——
也就是說，這 6 個專案之所以是 🟡 需人工複核而不是 🟢 未發現明顯風險，
唯一的理由是一段**使用者不會安裝到的程式碼**裡有 `eval(`。

---

## 那六個專案

| 專案 | 判定 | eval 證據 | 其他 HIGH |
|---|---|---|---|
| `ChromeDevTools/chrome-devtools-mcp` | 🟡 | `tests/devtools/DevtoolsUtils.test.ts`、`tests/tools/input.test.ts` | 無 |
| `MervinPraison/PraisonAI` | 🟡 | `examples/js/tools/basic-tools.ts`、`examples/js/tools/custom-tool.ts`、`examples/python/agents/math-agent.py` | 無 |
| `basicmachines-co/basic-memory` | 🟡 | `benchmarks/src/basic_memory_benchmarks/agent_tasks/models.py`、`.../llm/tool_agent.py` | 無 |
| `modelscope/FunASR` | 🟡 | `examples/industrial_data_pretraining/fun_asr_nano/demo2.py`、`.../model.py` | 無 |
| `alexalexalex222/frontend-design-loop-mcp` | 🟡 | `tests/test_mcp_code_server_selection.py` | 無 |
| `Dave-London/Pare` | 🟡 | `benchmarks/v2/scripts/benchmark-v2-mutating.ts` | npm 套件標示的倉庫與實際來源不一致 |

`Dave-London/Pare` 有另一個獨立的 HIGH，所以就算 eval 那項拿掉，它仍會是 🟡。
其餘五個會變成 🟢。

另外兩筆證據落在 `scripts/` 與 `site/`：

| 專案 | eval 證據 | 其他 HIGH |
|---|---|---|
| `DeusData/codebase-memory-mcp` | `scripts/extract_nomic_vectors.py`、`scripts/security-install.sh` | 無 |
| `homeassistant-ai/ha-mcp` | `site/scripts/a11y-audit.mjs` | 會讀寫本機檔案、會執行外部指令 |

**這兩筆我不主張歸成同一類。** `scripts/` 底下的東西未必不執行——
`security-install.sh` 這種名字反而更值得看，不是更不值得看。
列出來是為了讓分類的邊界公開，不是為了衝高數字。

---

## 為什麼這件事會被注意到

這不是靜態盤點出來的，是**三次巡檢連續踩到同一個樣態**才浮現的：

1. **08-31**：`basicmachines-co/basic-memory` 🟢→🟡，新增的 HIGH 證據在 `benchmarks/`。
   當時我驗證了規則命中的是呼叫而非檔名，判定為真實命中，但註記了「兩個命中都在 benchmarks/ 底下」。
2. **09-03**：`t8y2/dbx` 少掉同一個 HIGH，原證據是 `apps/desktop/src/__tests__/startupInputGuard.spec.ts`。
   上游改寫或刪掉了那個測試，一個 HIGH 就消失了。
3. **09-05**（本輪，重掃 `2da581a`）：`MervinPraison/PraisonAI` 少掉「setup.py 覆寫了安裝期指令」，
   但保留了 eval 那項——而它的證據是 `examples/` 底下三個檔案。

第三次之後才做了上面那份盤點。**單看任何一次都只是個案，三次才看得出這是取材範圍的問題。**

值得強調第 2 點的含意：`dbx` 的 HIGH 消失，不是因為它變安全了，
而是因為**上游動了一個測試檔**。一個安全結論如果會被測試檔的增刪推翻，
那它衡量的就不完全是使用者承擔的風險。

---

## 這代表什麼、不代表什麼

**不代表**這 28 筆有 8 筆是誤報。測試與範例碼裡的 `eval(` 確實存在，工具沒有看錯。
把它報出來也不是全無道理——範例碼常常被使用者原樣複製，基準碼有時會被打包進 sdist。

**代表**的是：標題寫的是「**超出宣稱用途**」，這句話對讀者的意思是
「這個工具做了它沒說要做的事」。當證據是 `examples/python/agents/math-agent.py` 時，
比較準確的說法是「這個**倉庫**裡有一段示範用的動態執行程式碼」——
那和「你安裝的這個 MCP 會動態執行程式碼」不是同一件事，而使用者是照後者在做決定的。

一個專案是 🟡 還是 🟢，是這個產品最外層、最多人只看這一眼的輸出。
目前有 5 個專案的這一眼，繫在使用者不會安裝的檔案上。

---

## 可能的選項（未實作，待共同開發者決定）

**A. 維持現狀。** 理由站得住：範例碼會被複製，基準碼可能被打包，寧可多報。
   若採此案，建議至少在文案上把證據路徑的性質講出來（見 D）。

**B. 評分時排除非出貨路徑。** 命中仍記錄，但不計入 HIGH／不影響 verdict。
   風險：路徑樣式是啟發式的，`scripts/` 這種邊界會判錯；且各語言慣例不同
   （Python 的 `tests/` 有時真的會被 `packages=find_packages()` 收進去）。

**C. 抓取時就不取這些路徑。** 最省事，但會讓其他規則也一起失明——
   測試檔裡的硬編碼憑證、範例碼裡的可疑主機，那些是真的想看到的。**不建議。**

**D. 只改文案，不改判定。** 當一筆 eval 命中的證據全落在非出貨路徑時，
   標題改成類似「倉庫的測試／範例碼中使用 eval」，嚴重度降一級或加註記。
   這是唯一落在 UI/UX 範圍內、我可以動手的選項——**但它需要後端在 finding 上多一個欄位
   標示證據性質，屬於 API 回傳結構的變更，依 UX-TASK-BRIEF §0 必須先提出並等待確認。**
   我沒有動它。

我的傾向是 **D 加上 B 的一部分**：先把事實講清楚（D），再決定要不要調整權重（B）。
但這是引擎維護者的決定，不是我的。

---

## 重現方式

```bash
# 以 reports/data.json 為準，把 eval 類 findings 按證據路徑分類
python3 - <<'PY'
import json,re
d=json.load(open('reports/data.json'))
STRICT=re.compile(r'(^|/)(tests?|__tests__|spec|specs|benchmarks?|examples?|samples?|demos?|fixtures?|e2e)(/|$)',re.I)
rows=[]
for p in d['projects']:
    for f in p.get('findings',[]):
        if 'eval' in f['title'].lower() or '動態執行' in f['title']:
            ev=[e.strip() for e in (f.get('evidence') or '').replace('、','\n').split('\n') if e.strip()]
            if ev: rows.append((p['slug'], p['verdict'], f['severity'], ev))
allnon=[r for r in rows if all(STRICT.search(e) for e in r[3])]
print(f'eval 類 findings {len(rows)} 筆，證據全在測試／基準／範例路徑的 {len(allnon)} 筆')
cur={p['slug']:p for p in d['projects']}
for slug,v,sev,ev in sorted(allnon):
    others=[f['title'] for f in cur[slug]['findings']
            if f['severity']=='HIGH' and 'eval' not in f['title'].lower() and '動態執行' not in f['title']]
    print(f'  {v[:2]} {slug}: {"、".join(ev)}  | 其他 HIGH: {others or "無"}')
PY
```

---

*發現時間：2026-09-05 03:15 UTC，於例行的六小時巡檢中合併每日重掃 `2da581a` 時。*
*發現的方式是同一個樣態在 08-31、09-03、09-05 三輪各出現一次；*
*前兩次都只在巡檢筆記記了一行，第三次才做全庫盤點。*
