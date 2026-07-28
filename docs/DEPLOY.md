# 網站部署與登入功能設定

網站本體是純靜態(`site/`),不設定任何東西也能完整瀏覽。
以下設定只影響**登入**與**提交掃描請求**兩個附加能力——
沒設定時網站自動降級:導覽列不顯示登入鈕,一切照常。

## 架構

```
site/            靜態頁(site.py 產出)
api/index.py     唯一的 serverless function,處理所有 /api/*
                 (GitHub OAuth 登入、session、提交掃描請求 → GitHub issue)
```

- **零第三方相依**:後端只用 Python 標準函式庫,與 CLI 工具同一立場。
- **無資料庫**:session 是 HMAC 簽名的 cookie;收藏清單存在使用者
  瀏覽器的 localStorage;掃描請求直接開成公開的 GitHub issue。
  我們拿不到的資料,就不必解釋怎麼保管。

## 一、建立 GitHub OAuth App

GitHub → Settings → Developer settings → **OAuth Apps** → New OAuth App:

| 欄位 | 值 |
|---|---|
| Application name | `mcp-guard 網站登入`(名稱任意) |
| Homepage URL | `https://mcp-guard-iota.vercel.app` |
| Authorization callback URL | `https://mcp-guard-iota.vercel.app/api/auth/callback` |

建立後記下 **Client ID**,並 Generate a new **client secret**。

> 登入流程不要求任何 scope——我們只需要「你是誰」,
> 不碰使用者的 repo、email 或任何資源。

## 二、設定 Vercel 環境變數

專案 → Settings → Environment Variables(全部 Production + Preview):

| 變數 | 值 |
|---|---|
| `GITHUB_CLIENT_ID` | OAuth App 的 Client ID |
| `GITHUB_CLIENT_SECRET` | OAuth App 的 Client Secret |
| `SESSION_SECRET` | 隨機字串:`openssl rand -hex 32` |
| `GITHUB_ISSUE_TOKEN` | (選)見下 |
| `ISSUE_REPO` | (選)接收掃描請求的 repo,預設 `rfobelieve-crypto/mcp-guard` |
| `SITE_ORIGIN` | (選)正式網域,預設 `https://mcp-guard-iota.vercel.app` |

`GITHUB_ISSUE_TOKEN` 供「提交掃描請求 / 回報誤判」開 issue 用。
建議用 **fine-grained PAT**,權限開到最小:

- Repository access:只選 `ISSUE_REPO` 那一個 repo
- Permissions:**Issues → Read and write**,其餘全不給

沒設定這個變數時,提交功能回應「尚未設定」,登入仍可用。

## 三、部署與驗證

```bash
python site.py        # 產出 site/
git push              # Vercel 自動部署(靜態 + api/)
```

部署後檢查:

1. `https://<網域>/api/me` → 未登入應回 `401 {"login": null}`
2. 導覽列出現「登入」→ 點擊走完 GitHub 授權 → 顯示頭像與帳號
3. 總表頁「提交掃描請求」→ 登入後送出 → 回傳 issue 連結
4. 安全 headers:`curl -sI https://<網域>/ | grep -i content-security`
   應看到 `script-src 'self'`(全站無行內 script)

## 安全設計備忘

- OAuth `state` 參數:隨機值存 10 分鐘的 HttpOnly cookie,callback 以
  `compare_digest` 核對——擋 CSRF。
- Session cookie:`HttpOnly; Secure; SameSite=Lax`,HMAC-SHA256 簽名,
  30 天過期,偽造或竄改即失效。
- `/api/submit` 另驗 `Origin` header,並以「同標題 open issue 查重」
  作為天然的防重複/限流。
- Host header 不回聲:redirect 只導向白名單網域(正式網域與
  `*.vercel.app` preview)。
- CSP `script-src 'self'`:頁面所有 script 都是外部檔,行內一律拒收。
