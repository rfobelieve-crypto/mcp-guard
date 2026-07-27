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

MAX_FILE_BYTES = 512 * 1024      # 單檔超過就跳過（不讀大二進位檔）
MAX_TOTAL_FILES = 400            # 掃描檔數上限，避免超大 repo 拖垮
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
            if not member.isfile() or len(files) >= MAX_TOTAL_FILES:
                continue
            if member.size > MAX_FILE_BYTES:
                continue
            # tarball 的第一層是 owner-repo-sha/，去掉它讓路徑好讀
            path = member.name.split("/", 1)[-1]
            if not path or "/." in f"/{path}":
                pass  # 隱藏檔仍收，設定檔常藏風險
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
    return b
