# 本機開發環境與日常流程（WSL）

給在 Windows 上開發的人。macOS／Linux 可直接跳到「二、取得專案」。

---

## 一、一次性設定

### 1. 安裝 WSL

以**系統管理員身分**開 PowerShell：

```powershell
wsl --install
```

裝完重開機，設定 Linux 使用者名稱與密碼（與 Windows 帳號無關）。
之後都在 **Windows Terminal → Ubuntu 分頁**操作。

> 為什麼是 WSL 而不是 CMD／PowerShell：這個專案的輸出全是繁體中文與
> emoji（`🔴 不要安裝`／`🟢 未發現明顯風險`），文件與指令也都是 bash 寫法。
> WSL 可以原封不動複製貼上；CMD 則要手動 `chcp 65001`、把每條指令翻譯成
> Windows 語法，翻錯了就是在 debug 一個本來不存在的問題。

### 2. 安裝工具

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl
```

`gh` 用官方來源（Ubuntu 內建版本常過舊）：

```bash
(type -p wget >/dev/null || sudo apt install wget -y) \
&& sudo mkdir -p -m 755 /etc/apt/keyrings \
&& wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
   | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
   | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update && sudo apt install gh -y
```

登入（**不能省**——未認證的 GitHub API 每小時只有 60 次額度，
稽核工具會一直失敗）：

```bash
gh auth login          # GitHub.com → HTTPS → Login with a web browser
gh auth status         # 確認顯示 ✓ Logged in
```

> WSL 沒有預設瀏覽器，`gh` 會說 `Failed opening a web browser`——正常。
> 自己把 https://github.com/login/device 貼到 Windows 瀏覽器、輸入畫面上的
> 代碼即可。想讓它自動開的話：
>
> ```bash
> sudo tee /usr/local/bin/wslview >/dev/null <<'EOF'
> #!/bin/sh
> exec explorer.exe "$@"
> EOF
> sudo chmod +x /usr/local/bin/wslview
> ```

---

## 二、取得專案

> ⚠️ **一定要放在 Linux 家目錄（`~`），不要放 `/mnt/c/...`**
> 跨檔案系統存取在 WSL 裡慢好幾倍，git 與測試都會明顯變慢。

```bash
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/rfobelieve-crypto/mcp-guard
cd mcp-guard
```

### 虛擬環境

Ubuntu 24.04 之後直接 `pip install .` 會被 PEP 668 擋下
（`externally-managed-environment`），用 venv：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

每次新開終端機都要先 `source ~/projects/mcp-guard/.venv/bin/activate`。

### 確認能跑

```bash
mcp-guard idosal/git-mcp
```

看到 `🟢 未發現明顯風險` 之類的結論，且中文與 emoji 顯示正常，就通了。

---

## 三、⚠️ 最重要的一個陷阱

`vercel.json` 裡 `buildCommand` 是空的、`outputDirectory` 是 `site`：

```json
{ "framework": null, "buildCommand": "", "outputDirectory": "site" }
```

**Vercel 直接部署 repo 裡已提交的 `site/` 資料夾，不會幫你建置。**

所以：

> **改了 `site.py` 之後，一定要跑 `python3 site.py` 並把 `site/` 一起提交，
> 否則網站完全不會變。**

同理，`reports/data.json` 更新後（例如合併每日重掃）也要重跑一次，
否則網頁顯示的內容會與資料對不上。

這是這個架構最容易犯的錯：程式碼改了、測試也過了、推上去了，
但網站沒動——因為部署的是產物，不是原始碼。

---

## 四、日常流程

### 開工前

```bash
cd ~/projects/mcp-guard
source .venv/bin/activate
git pull
git fetch origin main
git merge origin/main        # 併入 main 上的新進度
```

**若這一步帶進了 `reports/` 或 `site/` 的變動**（每日重掃就會）：

```bash
python3 site.py              # 讓產物與資料一致
```

### 改完之後（推送前的固定四步）

```bash
python3 site.py                    # 1. 只要動過 site.py 或 reports/ 就要跑
python3 -m tests.test_poisoning    # 2. 紅隊測試 38 項
python3 -m tests.test_lookup       #    身分查詢失敗模式 3 項
python3 -m tests.test_userinput    #    輸入正規化 16 項
python3 -m tests.test_routing      #    API 路由 10 項
git add -A && git commit -m "說明改了什麼"
git push
```

四套測試都必須是綠的才推。理由與 `daily-scan.yml` 裡寫的一樣：

> 一個連自己紅隊測試都沒過的掃描器，不該對外發布任何結論。

---

## 五、push 之後會自動發生什麼

**這一段完全不用手動做。** 推上去之後：

| 推到哪 | 自動發生 |
|---|---|
| 任何分支 | Vercel 建 **preview 部署**，並把網址貼到對應的 PR |
| `main` | Vercel 更新**正式站** https://mcp-guard-iota.vercel.app |
| （每天 05:00 台北時間） | GitHub Actions 重掃 178 個專案 → 重建網站 → 寫回 repo → 發布 GitHub Pages |

每日重掃的流程刻意把紅隊測試放在掃描**之前**，沒過就整個中止，
不會發布任何結論。

### 唯一需要你手動做的：`git push`

git 不會自己推。**這是刻意的**：自動推送等於把還沒測過的狀態直接送到
合作夥伴的 repo 與正式站。

如果想要多一層保險，可以裝一個 pre-push hook，讓沒過測試的推送直接被擋下：

```bash
cat > .git/hooks/pre-push <<'EOF'
#!/bin/sh
# 推送前跑一次四套測試,沒過就擋下。
# 與 daily-scan.yml 同一個原則:沒過測試就不該對外發布。
cd "$(git rev-parse --show-toplevel)" || exit 1
[ -f .venv/bin/activate ] && . .venv/bin/activate
for t in test_poisoning test_lookup test_userinput test_routing; do
  if ! python3 -m tests.$t >/dev/null 2>&1; then
    echo "✗ tests.$t 未通過,推送已中止。"
    echo "  自己跑一次看細節:python3 -m tests.$t"
    exit 1
  fi
done
echo "✓ 四套測試通過"
EOF
chmod +x .git/hooks/pre-push
```

> git hooks 不會被 clone 帶走，所以這是每台機器各自裝一次的東西。
> 真的需要繞過時：`git push --no-verify`。

---

## 六、與合作夥伴同時開發

`main` 上有共同開發者在推進，加上每日重掃會自動 push，所以 `main`
經常前進。處理原則：

1. **開工前先 `git merge origin/main`**，不要累積太多再一次合。
2. **有衝突時以 `main` 的架構為準**——把自己這邊的加值移植上去，
   不要用自己的版本覆蓋對方的決定。
3. `site/` 底下的衝突不必手動解：取 `main` 的版本，然後重跑
   `python3 site.py` 重新產生即可（那是產物，不是原始碼）。

```bash
git checkout --theirs site/ && python3 site.py && git add -A
```

---

## 七、需要環境變數的部分

網站本體（靜態頁）不需要任何設定。以下只影響附加功能，
設定方式見 [`DEPLOY.md`](DEPLOY.md)：

| 變數 | 影響 |
|---|---|
| `GITHUB_TOKEN` | 首頁查詢框的**即時掃描**。沒設的話 GitHub 只給每小時 60 次未認證額度，幾乎必定失敗 |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` / `SESSION_SECRET` | 登入功能 |
| `GITHUB_ISSUE_TOKEN` | 「提交掃描請求 / 回報誤判」開 issue |

本機要測 `/api/scan` 的話：

```bash
export GITHUB_TOKEN=你的_token
python3 -m mcp_guard owner/repo
```

---

## 八、離線備份

GitHub 與 Vercel 是**運作**環境，不是**保險**——Vercel 部署的來源就是那個
倉庫，所以倉庫被刪、帳號登不進去、或被誤 force-push 時，兩者會一起消失。

```bash
python3 make_backup.py --verify
```

產出 `backup/`（已在 `.gitignore` 內，不會進版控）：

| 檔案 | 內容 | 約略大小 |
|---|---|---|
| `mcp-guard-source.tgz` | 全部原始碼、四套測試、文件、workflow、字型與機器人素材 | 240 KB |
| `data.json.gz` | 178 個專案的完整掃描結果 | 88 KB |

刻意不含 `site/`、`reports/*.md`、`assets/og/*.jpg`、`robot_a.png`——
那些都能重建，而**備份的體積直接決定它多久被更新一次**。
`data.json` 是唯一不可再生的部分：沒有 GitHub 存取與 11 分鐘就重跑不出來。

`--verify` 會解到暫存目錄、重建網站、與正式產物逐位元組比對，再跑完四套
測試。沒有實際還原過的備份只是一個「看起來像備份的檔案」，所以平常就加著跑。

還原方式寫在 Google Drive 的〈mcp-guard 離線備份 — 還原說明〉裡，
指令與這份文件第二、三節相同。

---

## 九、常用指令速查

```bash
mcp-guard owner/repo                 # 掃單一專案
mcp-guard https://github.com/o/r     # 貼網址亦可
mcp-guard npm:套件名                  # 從 npm 反查原始碼
mcp-guard owner/repo --md 報告.md     # 輸出完整 Markdown
mcp-guard owner/repo --quiet         # 只印結論行

python3 site.py                      # 重新產生網站（約 0.3 秒）
python3 batch.py                     # 重掃 targets.txt 全部（約 11 分鐘）
python3 sync_targets.py              # 從官方 registry 同步名單

python3 -m tests.test_poisoning      # 紅隊測試
python3 -m tests.test_lookup         # 身分查詢失敗模式
python3 -m tests.test_userinput      # 輸入正規化
python3 -m tests.test_routing        # API 路由（cleanUrls/trailingSlash/rewrites）

python3 make_backup.py --verify      # 產生離線備份並實際還原驗證
```

CLI 退出碼（可接進 CI）：`0` 無明顯風險／`1` 有嚴重或多項高風險／`2` 抓取失敗。
