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
import re
import subprocess
import tarfile
from dataclasses import dataclass, field

import urllib.request

from . import agentfiles

MAX_FILE_BYTES = 512 * 1024      # 單檔超過就跳過（不讀大二進位檔）
MAX_TOTAL_FILES = 400            # 掃描檔數上限，避免超大 repo 拖垮

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
    notes: list[str] = field(default_factory=list)


def _gh(args: list[str]) -> tuple[int, bytes, str]:
    """呼叫 gh CLI。回傳 (returncode, stdout_bytes, stderr_text)。"""
    try:
        p = subprocess.run(["gh", *args], capture_output=True, timeout=120)
    except FileNotFoundError as e:
        raise FetchError("找不到 gh CLI，請先安裝並執行 gh auth login") from e
    except subprocess.TimeoutExpired as e:
        raise FetchError("gh CLI 逾時") from e
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace")


def gh_json(path: str) -> dict | None:
    """GET 一個 GitHub API 端點，404 回 None。"""
    code, out, _err = _gh(["api", path])
    if code != 0:
        return None
    try:
        return json.loads(out.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return None


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

    meta = gh_json(f"repos/{slug}")
    if meta:
        b.exists, b.meta, b.owner_exists = True, meta, True
    else:
        b.exists = False
        owner = slug.split("/")[0]
        b.owner_exists = gh_json(f"users/{owner}") is not None
        return b   # repo 不存在就沒有原始碼可掃

    # 若是從 repo 進來的，回頭補查 npm（package.json 的 name）
    if kind == "repo":
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
