# -*- coding: utf-8 -*-
"""抓取層：GitHub / npm 的唯讀取得。

安全原則：
- 全程唯讀，**不執行**目標專案的任何程式碼。
- 原始碼以 tarball 取得後「在記憶體中」解析，不落地解壓，
  因此不存在 zip-slip / path traversal 風險。
"""
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import tarfile
from dataclasses import dataclass, field

import urllib.error
import urllib.parse
import urllib.request

from . import agentfiles

MAX_FILE_BYTES = 512 * 1024      # 單檔超過就跳過（不讀大二進位檔）
MAX_TOTAL_FILES = 400            # 掃描檔數上限，避免超大 repo 拖垮
# 原始碼壓縮檔是整個讀進記憶體再解析的（刻意不落地，避免 zip-slip）。
# 名單從官方 registry 同步後會掃到 netdata 這種等級的專案，沒有上限的話
# 一個目標就能把記憶體吃光。超過就跳過原始碼，身分與維護檢查照跑。
MAX_REPO_KB = 400 * 1024         # GitHub 回報的 repo 大小（KB），約 400MB

# 供應鏈檢查的核心輸入。這些檔案**不受檔數上限限制**。
#
# 2026-07-28：modelcontextprotocol/inspector 前一輪掃出 2 個供應鏈發現，
# 下一輪變成 0——它有 400+ 個檔案，而 tarball 的檔案順序並不保證穩定，
# package.json 剛好被一般原始碼擠出上限。對每日重掃的產品來說，這比漏報
# 更糟：同一個專案在不同日期會給出不同結論，報告就不可信了。
MANIFEST_NAMES = frozenset({
    "package.json", "pyproject.toml", "setup.py", "setup.cfg",
    "requirements.txt", "pipfile", "poetry.lock",
    "go.mod", "cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts",
    "gemfile", "composer.json", "pubspec.yaml",
})
TEXT_EXT = {
    ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".toml",
    ".md", ".yaml", ".yml", ".cfg", ".ini", ".txt", ".sh", ".rb", ".go",
}


class FetchError(RuntimeError):
    pass


@dataclass
class RepoBundle:
    """一個待驗證目標的所有唯讀事實。"""
    slug: str                                  # owner/repo
    exists: bool = False
    owner_exists: bool = False
    meta: dict = field(default_factory=dict)   # GitHub repo API 原始回應
    files: dict[str, str] = field(default_factory=dict)   # 路徑 -> 內容
    npm: dict = field(default_factory=dict)    # npm registry 回應（若有）
    npm_name: str = ""
    pypi: dict = field(default_factory=dict)   # PyPI 回應（若有）
    pypi_name: str = ""
    registry: dict = field(default_factory=dict)  # 官方 registry 的登錄資訊
    notes: list[str] = field(default_factory=list)


API_ROOT = "https://api.github.com/"


class _NoAuthOnHostChange(urllib.request.HTTPRedirectHandler):
    """換主機時把 Authorization 拿掉。

    tarball 端點會 302 到 codeload.github.com。urllib 預設會把原始標頭
    一起帶過去——對一個稽核工具來說，把自己的 token 跟著轉址送出去
    是最不該犯的錯，即使這次的目的地剛好也是 GitHub 自己。
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is None:
            return None
        if urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(
                req.full_url).netloc:
            new.headers = {k: v for k, v in new.headers.items()
                           if k.lower() != "authorization"}
        return new


def _token() -> str:
    """從環境變數取 GitHub token。取不到回空字串（改用未認證額度）。"""
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        tok = os.environ.get(name, "").strip()
        if tok:
            return tok
    return ""


def _http_api(path: str) -> tuple[int, bytes, str]:
    """直接打 GitHub REST API，不經過 gh CLI。

    存在的理由是 serverless：那裡沒有 gh 這個執行檔，但隨選掃描要能跑。
    回傳格式刻意與 _gh 一致，讓上層一個字都不用改。
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "mcp-guard",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    tok = _token()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"

    opener = urllib.request.build_opener(_NoAuthOnHostChange)
    req = urllib.request.Request(API_ROOT + path.lstrip("/"), headers=headers)
    try:
        with opener.open(req, timeout=60) as r:
            return 0, r.read(), ""
    except urllib.error.HTTPError as e:
        # 404 是有意義的答案（repo 不存在），不是故障——與 gh 的行為一致，
        # 交給上層用非零 returncode 判讀。
        return 1, b"", f"HTTP {e.code} {path}"
    except Exception as e:                                # noqa: BLE001
        return 1, b"", f"{type(e).__name__}: {e}"


def _gh(args: list[str]) -> tuple[int, bytes, str]:
    """呼叫 gh CLI；環境裡沒有 gh 就退回直接打 REST API。

    順序刻意是「先 CLI、後 HTTP」：本機與 CI 都有 gh，沿用它既有的認證，
    每日重掃的行為因此與加上這段之前完全相同。HTTP 只在 gh 不存在時才會
    被用到（例如 serverless 的隨選掃描）。
    """
    try:
        p = subprocess.run(["gh", *args], capture_output=True, timeout=120)
    except FileNotFoundError:
        if len(args) == 2 and args[0] == "api":
            return _http_api(args[1])
        raise FetchError("找不到 gh CLI，請先安裝並執行 gh auth login")
    except subprocess.TimeoutExpired as e:
        raise FetchError("gh CLI 逾時") from e
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


def gh_json(path: str) -> dict | None:
    """GET 一個 GitHub API 端點，查不到或失敗都回 None。"""
    return gh_json_ex(path)[0]


def gh_json_ex(path: str) -> tuple[dict | None, str]:
    """同 gh_json，但一併回報**為什麼**沒拿到資料。

    狀態值：`ok`（拿到了）、`missing`（確定是 404）、`error`（其他失敗）。

    區分這兩種失敗是必要的，不是潔癖：上層用「拿不到 repo」推導出
    「這個 repo 不存在」，而那個結論會直接變成 🔴 不要安裝。若把限流
    （403）、逾時、5xx 全部當成 404，就會對一個好端端的專案發出
    「倉庫與作者帳號都不存在」的指控，證據欄還寫著一個從未發生的 404。
    對真實專案的不實指控，傷害不比漏報小。
    """
    code, out, err = _gh(["api", path])
    if code == 0:
        try:
            return json.loads(out.decode("utf-8", "replace")), "ok"
        except json.JSONDecodeError:
            return None, "error"
    # gh CLI 的 404 訊息形如 "gh: Not Found (HTTP 404)"；
    # _http_api 的形如 "HTTP 404 <path>"。兩者都涵蓋。
    blob = f"{err} {out.decode('utf-8', 'replace')[:200]}"
    if "404" in blob or "Not Found" in blob:
        return None, "missing"
    return None, "error"


def parse_target(raw: str) -> tuple[str, str]:
    """把使用者輸入正規化成 (kind, value)。

    支援：owner/repo、github 網址、npm:package、裸 npm 套件名。
    """
    s = raw.strip().rstrip("/")
    if s.startswith("npm:"):
        return "npm", s[4:].strip()
    m = re.search(r"github\.com[/:]([^/]+/[^/#?]+)", s)
    if m:
        return "repo", m.group(1).removesuffix(".git")
    if re.fullmatch(r"[\w.-]+/[\w.-]+", s):
        return "repo", s
    return "npm", s


def fetch_npm(name: str) -> dict:
    """讀 npm registry（公開、免認證）。查無回空 dict。"""
    url = f"https://registry.npmjs.org/{name.replace('/', '%2f')}"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return {}


def fetch_pypi(name: str) -> dict:
    """讀 PyPI（公開、免認證）。查無回空 dict。"""
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return {}


# 套件名稱的三種宣告方式。刻意用正則而非 tomllib：後者要 Python 3.11，
# 而本套件宣告支援 3.9——為了讀一個欄位就抬高執行環境需求並不划算。
_PYNAME_PATTERNS = (
    ("pyproject.toml", re.compile(
        r"^\s*\[project\][^\[]*?^\s*name\s*=\s*[\"']([^\"']+)",
        re.M | re.S)),
    ("setup.cfg", re.compile(
        r"^\s*\[metadata\][^\[]*?^\s*name\s*=\s*([^\s#]+)", re.M | re.S)),
    ("setup.py", re.compile(r"""\bname\s*=\s*["']([^"']+)""")),
)


def python_package_name(files: dict[str, str]) -> str:
    """從專案檔案推出 PyPI 套件名；推不出來回空字串。"""
    for path, pat in _PYNAME_PATTERNS:
        text = files.get(path)
        if not text:
            continue
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return ""


def _repo_from_npm(doc: dict) -> str:
    """從 npm metadata 反查 GitHub slug。"""
    latest = (doc.get("dist-tags") or {}).get("latest")
    ver = ((doc.get("versions") or {}).get(latest)) or {}
    for src in (ver.get("repository"), doc.get("repository")):
        if isinstance(src, dict):
            src = src.get("url", "")
        if isinstance(src, str) and src:
            m = re.search(r"github\.com[/:]([^/]+/[^/#?]+)", src)
            if m:
                return m.group(1).removesuffix(".git")
    return ""


def fetch_source(slug: str) -> dict[str, str]:
    """下載 tarball 並在記憶體中讀出文字檔。不落地、不執行。"""
    code, blob, err = _gh(["api", f"repos/{slug}/tarball"])
    if code != 0 or not blob:
        raise FetchError(f"無法取得原始碼壓縮檔：{err.strip()[:200]}")
    files: dict[str, str] = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        for member in tf:
            if not member.isfile():
                continue
            if member.size > MAX_FILE_BYTES:
                continue
            # tarball 的第一層是 owner-repo-sha/，去掉它讓路徑好讀
            path = member.name.split("/", 1)[-1]
            if not path or "/." in f"/{path}":
                pass  # 隱藏檔仍收，設定檔常藏風險
            # 代理指令檔與打包宣告檔一律收：前者是投毒的主要落點，後者是
            # 供應鏈檢查的唯一輸入。若被大型 repo 的一般原始碼擠出檔數上限，
            # 或因為沒有副檔名而落在 TEXT_EXT 之外，就是靜默漏報。
            name = path.rsplit("/", 1)[-1].lower()
            if not agentfiles.kind(path) and name not in MANIFEST_NAMES:
                if len(files) >= MAX_TOTAL_FILES:
                    continue
                if "." + path.rsplit(".", 1)[-1] not in TEXT_EXT:
                    continue
            try:
                data = tf.extractfile(member)
                if data is None:
                    continue
                files[path] = data.read().decode("utf-8", "replace")
            except Exception:
                continue
    return files


def collect(raw_target: str) -> RepoBundle:
    """把一個輸入目標收斂成 RepoBundle（全部唯讀事實）。"""
    kind, value = parse_target(raw_target)
    slug, npm_name, npm_doc = "", "", {}

    if kind == "npm":
        npm_name = value
        npm_doc = fetch_npm(value)
        slug = _repo_from_npm(npm_doc)
    else:
        slug = value

    b = RepoBundle(slug=slug, npm=npm_doc, npm_name=npm_name)

    if kind == "npm" and not npm_doc:
        b.notes.append(f"npm registry 查無套件 {value}")
    if not slug:
        b.notes.append("無法對應到任何 GitHub repo")
        return b

    meta, status = gh_json_ex(f"repos/{slug}")
    if meta:
        b.exists, b.meta, b.owner_exists = True, meta, True
    elif status == "missing":
        b.exists = False
        owner = slug.split("/")[0]
        owner_meta, owner_status = gh_json_ex(f"users/{owner}")
        if owner_status == "error":
            # repo 確定不存在，但作者查不動。兩種措辭的嚴厲程度差很多
            # （「連帳號都沒註冊過」vs「repo 已刪除或轉私有」），
            # 沒把握就不要選比較重的那一句。
            raise FetchError(
                f"已確認 repo {slug} 不存在，但無法查證作者帳號 "
                f"{owner} 是否存在，因此不產生結論。請稍後再試。")
        b.owner_exists = owner_meta is not None
        return b   # repo 不存在就沒有原始碼可掃
    else:
        # 查不動 ≠ 不存在。這裡刻意不產生任何結論，讓它走既有的
        # 「抓取失敗」通道（CLI 退出碼 2），而不是給一個看似乾淨的
        # 🟢，也不是給一個毀人清譽的 🔴。
        raise FetchError(
            f"無法向 GitHub 確認 {slug} 是否存在（API 回應異常，"
            "可能是限流或網路問題）。未取得可信事實，因此不產生結論。")

    size_kb = meta.get("size") or 0
    too_big = size_kb > MAX_REPO_KB

    # 若是從 repo 進來的，回頭補查 npm（package.json 的 name）
    if kind == "repo":
        if too_big:
            b.notes.append(
                f"倉庫過大（約 {size_kb / 1024:.0f} MB），已略過原始碼掃描："
                "權限、投毒、供應鏈這幾項因此不完整，請自行檢視原始碼。")
        else:
            try:
                b.files = fetch_source(slug)
            except FetchError as e:
                b.notes.append(str(e))
        pkg = b.files.get("package.json")
        if pkg:
            try:
                name = json.loads(pkg).get("name", "")
            except json.JSONDecodeError:
                name = ""
            if name:
                b.npm_name = name
                b.npm = fetch_npm(name)
    elif too_big:
        b.notes.append(
            f"倉庫過大（約 {size_kb / 1024:.0f} MB），已略過原始碼掃描。")
    else:
        try:
            b.files = fetch_source(slug)
        except FetchError as e:
            b.notes.append(str(e))

    # Python 生態：MCP 官方 SDK 有 Python 版，只查 npm 等於漏掉一半生態，
    # 而 pip install 會**直接執行 setup.py**——那是比 postinstall 更少人
    # 知道的安裝期程式碼執行點。
    pyname = python_package_name(b.files)
    if pyname:
        b.pypi_name = pyname
        b.pypi = fetch_pypi(pyname)
    return b
