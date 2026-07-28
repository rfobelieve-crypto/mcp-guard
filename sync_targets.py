# -*- coding: utf-8 -*-
"""從官方 MCP registry 同步掃描名單。

registry.modelcontextprotocol.io 是官方註冊表，但它只回答「有哪些 MCP」，
不回答「哪個能裝」——那正是本專案要補的空白。這支腳本把它的清單轉成
掃描名單。

規模現實：registry 有兩萬多筆（含歷史版本）、約 13,800 個不重複的 GitHub
專案。全掃一輪要下載上萬個原始碼壓縮檔，對每日 CI 不切實際，因此名單由
三部分組成：

  1. 核心名單    手動維護（batch.py 的 TARGETS），不論星數都必掃。
                 裡面有刻意納入的低星專案——權限天生就大的類型。
  2. 星數前段    registry 全體依星數排序取前 N。
  3. 領域配額    只靠星數排序，名單會清一色是熱門開發工具：金融只有 3 個、
                 健康 2 個。但使用者的問題是「我要做交易策略該裝什麼」，
                 那類專案星數天生就低。因此再用 registry 的搜尋補上各領域
                 的代表，每個領域取固定配額。

用法：
    python sync_targets.py                 # 產生 targets.txt
    python sync_targets.py --limit 150     # 星數前段取更多
    python sync_targets.py --min-stars 200 # 改用星數門檻
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures as cf
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "targets.txt"
META = ROOT / "reports" / "registry_meta.json"
REGISTRY = "https://registry.modelcontextprotocol.io/v0/servers"
META_KEY = "io.modelcontextprotocol.registry/official"
BATCH = 100         # 每批 GraphQL 查詢的專案數
WORKERS = 4         # 並發批次數。再高會踩到 GitHub 的次級速率限制
MAX_PAGES = 2000    # 分頁上限：cursor 若沒有正常結束，不能無限打下去


def fetch_registry() -> dict[str, str]:
    """回傳 {owner/repo: 該專案在 registry 上的名稱}。只取最新版。"""
    seen: dict[str, str] = {}
    cursor, pages = None, 0
    while True:
        url = f"{REGISTRY}?limit=100"
        if cursor:
            url += "&cursor=" + urllib.parse.quote(cursor)
        with urllib.request.urlopen(url, timeout=60) as r:
            doc = json.loads(r.read().decode("utf-8", "replace"))
        for entry in doc.get("servers", []):
            meta = (entry.get("_meta") or {}).get(META_KEY) or {}
            if not meta.get("isLatest"):
                continue          # registry 會保留每個歷史版本，只要最新的
            sv = entry.get("server") or {}
            repo = sv.get("repository") or {}
            if repo.get("source") != "github":
                continue
            url_ = (repo.get("url") or "").strip()
            if "github.com/" not in url_:
                continue
            slug = url_.split("github.com/")[-1].strip("/").removesuffix(".git")
            if slug.count("/") == 1 and all(slug.split("/")):
                seen.setdefault(slug, sv.get("name", ""))
        cursor = (doc.get("metadata") or {}).get("nextCursor")
        pages += 1
        print(f"\r  讀取 registry… 第 {pages} 頁，已收集 {len(seen):,} 個專案",
              end="", file=sys.stderr, flush=True)
        if not cursor or pages >= MAX_PAGES:
            break
    print(file=sys.stderr)
    if pages >= MAX_PAGES:
        print(f"⚠ 已達分頁上限 {MAX_PAGES}，名單可能不完整", file=sys.stderr)
    return seen


# 依「星數前 N」取樣會讓名單全是熱門開發工具：金融只有 3 個、健康 2 個。
# 但使用者的問題是「我要做交易策略該裝什麼」，那類專案星數天生就低。
# 因此再用 registry 的搜尋補上各領域的代表，每個領域取固定配額。
DOMAIN_QUERIES = {
    "finance": ["trading", "finance", "crypto", "stock market", "payment"],
    "health": ["health", "medical", "fitness", "nutrition"],
    "data": ["analytics", "chart", "visualization", "dashboard"],
    "web": ["website", "frontend", "web design", "cms"],
    "media": ["image generation", "video", "audio", "design"],
    "productivity": ["notion", "slack", "calendar", "email", "task"],
    "research": ["arxiv", "research", "academic paper"],
    "infra": ["kubernetes", "monitoring", "deployment", "docker"],
}
DOMAIN_QUOTA = 10          # 每個領域最多補幾個（依星數）


def search_registry(query: str) -> dict[str, str]:
    """用 registry 的 search 找特定主題的專案。"""
    url = (f"{REGISTRY}?limit=100&search={urllib.parse.quote(query)}")
    try:
        with urllib.request.urlopen(url, timeout=45) as r:
            doc = json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return {}
    out = {}
    for entry in doc.get("servers", []):
        meta = (entry.get("_meta") or {}).get(META_KEY) or {}
        if not meta.get("isLatest"):
            continue
        sv = entry.get("server") or {}
        repo = sv.get("repository") or {}
        if repo.get("source") != "github":
            continue
        url_ = (repo.get("url") or "").strip()
        if "github.com/" not in url_:
            continue
        slug = url_.split("github.com/")[-1].strip("/").removesuffix(".git")
        if slug.count("/") == 1 and all(slug.split("/")):
            out.setdefault(slug, sv.get("name", ""))
    return out


def _gh_token() -> str:
    p = subprocess.run(["gh", "auth", "token"], capture_output=True, timeout=60)
    tok = p.stdout.decode("utf-8", "replace").strip()
    if not tok:
        raise SystemExit("取不到 GitHub token，請先執行：gh auth login")
    return tok


def _graphql(query: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "mcp-guard-sync"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


# repo 名稱的合法字元。registry 上的 URL 什麼都有，先濾掉不可能存在的，
# 免得拿它們去問 GitHub。
VALID_SLUG = __import__("re").compile(r"^[A-Za-z0-9._-]{1,100}/[A-Za-z0-9._-]{1,100}$")


def repo_stats(slugs: list[str]) -> dict[str, dict]:
    """批次查星數。

    一萬多個專案若逐一打 REST 就是一萬多次請求；改用 GraphQL 一次問 100 個，
    並且直接打 API 而不是每批都啟動一次 gh（那個程序啟動開銷本身就佔了大半
    時間）。批次查詢的 rate limit 成本是每批 1 point，不是每個專案 1 point。
    """
    token = _gh_token()
    slugs = [s for s in slugs if VALID_SLUG.match(s)]
    chunks = [slugs[i:i + BATCH] for i in range(0, len(slugs), BATCH)]
    out: dict[str, dict] = {}
    done = 0
    failed: list[str] = []

    def one(chunk: list[str]) -> dict[str, dict]:
        parts = []
        for j, s in enumerate(chunk):
            owner, name = s.split("/", 1)
            # GraphQL 的別名只能是英數與底線
            parts.append(f'r{j}: repository(owner:"{owner}", name:"{name}")'
                         "{ nameWithOwner stargazerCount pushedAt isArchived }")
        query = "{" + " ".join(parts) + "}"
        # 整批失敗過去是被靜默吞掉的，結果一批 100 個全被記成「查無」——
        # 那會讓名單看起來像是「registry 有一半的 repo 都消失了」。
        # 重試，而且失敗要講出來。
        for attempt in range(3):
            try:
                doc = _graphql(query, token)
                return {v["nameWithOwner"]: v
                        for v in (doc.get("data") or {}).values()
                        if v and v.get("nameWithOwner")}
            except Exception as e:
                if attempt == 2:
                    failed.append(f"{chunk[0]}…（{type(e).__name__}: {e}）")
                    return {}
                time.sleep(2 ** attempt * 1.5)
        return {}

    with cf.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for got in pool.map(one, chunks):
            out.update(got)
            done += 1
            print(f"\r  查詢星數… {min(done * BATCH, len(slugs)):,}/{len(slugs):,}"
                  f"（成功 {len(out):,}）", end="", file=sys.stderr, flush=True)
    print(file=sys.stderr)
    if failed:
        print(f"⚠ 有 {len(failed)} 批查詢重試後仍失敗，這些專案會被當成查無：",
              file=sys.stderr)
        for f in failed[:5]:
            print(f"    {f}", file=sys.stderr)
    return out


# registry 的命名空間本身就是驗證強度，這是可查證的事實、不是我們的評價：
#   io.modelcontextprotocol/*  官方團隊自己發布
#   <反轉網域>/*               發布者以 DNS TXT 證明擁有該網域（通常是公司）
#   io.github.<帳號>/*         只證明擁有那個 GitHub 帳號
# 對使用者來說差別很實際：com.microsoft 和 io.github.某人 的份量並不相同。
NS_RANK = {"official": 0, "domain": 1, "github": 2}


def namespace_kind(reg_name: str) -> tuple[str, str]:
    ns = (reg_name or "").split("/")[0].lower()
    if ns == "io.modelcontextprotocol":
        return "official", "MCP 官方發布"
    if ns.startswith("io.github."):
        return "github", "GitHub 帳號驗證"
    if "." in ns:
        return "domain", "網域驗證"
    return "github", "GitHub 帳號驗證"


def core_targets() -> list[str]:
    """手動維護的核心名單：不論星數都必掃。"""
    try:
        sys.path.insert(0, str(ROOT))
        import batch
        return list(batch.TARGETS)
    except Exception:
        return []


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="從官方 MCP registry 同步掃描名單")
    ap.add_argument("--limit", type=int, default=80,
                    help="核心名單之外最多取幾個（預設 80）")
    ap.add_argument("--min-stars", type=int, default=0,
                    help="星數門檻；設了就以此為準，limit 仍是上限")
    ap.add_argument("--domains-only", action="store_true",
                    help="只補領域配額，沿用現有 targets.txt 的星數前段"
                         "（跳過全量分頁，約 2 分鐘而非 40 分鐘）")
    args = ap.parse_args()

    # 全量分頁要走六百多頁、耗時數十分鐘，但星數前段其實變動很慢。
    # 只要沒有要重排星數名次，就不必每次都重掃一遍 registry。
    if args.domains_only:
        if not OUT.exists():
            raise SystemExit("--domains-only 需要既有的 targets.txt，"
                             "請先完整跑一次 sync_targets.py")
        existing = [ln.split("#", 1)[0].strip()
                    for ln in OUT.read_text(encoding="utf-8").splitlines()]
        existing = [s for s in existing if s]
        found = {}
        if META.exists():
            old = json.loads(META.read_text(encoding="utf-8")).get("servers", {})
            found = {s: v.get("name", "") for s, v in old.items()
                     if v.get("registered")}
        core = core_targets()
        picked = [s for s in existing if s not in core]
        stats = repo_stats(existing)
        print(f"沿用既有名單：核心 {len(core)} + 星數前段 {len(picked)}")
    else:
        found = fetch_registry()
        core = core_targets()
        print(f"registry 上有 {len(found)} 個不重複的 GitHub 專案"
              f"｜核心名單 {len(core)} 個")
        stats = repo_stats(sorted(set(found) | set(core)))

    # GraphQL 偶爾會有零星批次拿不到結果。同步名單裡少幾個無所謂（本來就是
    # 取前段），但核心名單顯示「查無」會直接誤導——那些是我們自己挑的專案。
    # 數量少，用 REST 補一次。
    for slug in core:
        if slug in stats:
            continue
        p = subprocess.run(["gh", "api", f"repos/{slug}"],
                           capture_output=True, timeout=90)
        try:
            m = json.loads(p.stdout.decode("utf-8", "replace") or "{}")
        except json.JSONDecodeError:
            continue
        if m.get("full_name"):
            stats[slug] = {"nameWithOwner": m["full_name"],
                           "stargazerCount": m.get("stargazers_count", 0),
                           "pushedAt": m.get("pushed_at", ""),
                           "isArchived": m.get("archived", False)}
            print(f"  （核心名單 {slug} 改用 REST 補查）", file=sys.stderr)
    print(f"其中 {len(stats)} 個目前仍存在於 GitHub"
          f"（{len(found) - len(stats) + len(core)} 個查無，已排除）")

    if not args.domains_only:
        ranked = sorted((s for s in stats if s not in core),
                        key=lambda s: -stats[s]["stargazerCount"])
        if args.min_stars:
            ranked = [s for s in ranked
                      if stats[s]["stargazerCount"] >= args.min_stars]
        picked = ranked[:args.limit]

    # 領域配額：星數排序天生偏向熱門開發工具，「我要做交易策略」這類
    # 需求對應的專案星數低，不補就永遠進不了名單。
    taken = set(core) | set(picked)
    by_domain: dict[str, list[str]] = {}
    for dom, queries in DOMAIN_QUERIES.items():
        found_dom: dict[str, str] = {}
        for q in queries:
            found_dom.update(search_registry(q))
            time.sleep(0.2)
        print(f"\r  領域補充… {dom}（搜到 {len(found_dom)} 個）",
              end="", file=sys.stderr, flush=True)
        cand = [s for s in found_dom if s not in taken and VALID_SLUG.match(s)]
        # 這些多半不在主查詢的 stats 裡，補查一次星數再排序
        extra = repo_stats(cand) if cand else {}
        stats.update(extra)
        top = sorted((s for s in cand if s in stats),
                     key=lambda s: -stats[s]["stargazerCount"])[:DOMAIN_QUOTA]
        by_domain[dom] = top
        taken.update(top)
        found.update({s: found_dom[s] for s in top})
    print(file=sys.stderr)
    domain_picked = [s for tops in by_domain.values() for s in tops]

    when = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# MCP 掃描名單",
        "#",
        f"# 由 sync_targets.py 於 {when} 從官方 registry 同步",
        f"# （registry.modelcontextprotocol.io，共 {len(found)} 個 GitHub 專案）",
        "#",
        "# 前段是手動維護的核心名單：不論星數都必掃，其中有些是刻意納入的",
        "# 低星專案——權限天生就大的類型，正是最需要在安裝前看懂的。",
        "# 後段依星數排序自動同步。要改核心名單請編輯 batch.py 的 TARGETS。",
        "",
        "# ── 核心名單 ──",
    ]
    for s in core:
        st = stats.get(s)
        star = f"★{st['stargazerCount']:,}" if st else "（查無）"
        lines.append(f"{s:<46} # {star}")
    lines += ["", f"# ── registry 同步（星數前 {len(picked)}）──"]
    for s in picked:
        lines.append(f"{s:<46} # ★{stats[s]['stargazerCount']:,}")
    if domain_picked:
        lines += ["", "# ── 領域配額（星數排序收不到，但使用者實際會問的類型）──"]
        for dom, tops in by_domain.items():
            if not tops:
                continue
            lines.append(f"# {dom}")
            for s in tops:
                lines.append(f"{s:<46} # ★{stats[s]['stargazerCount']:,}")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # 發布者身分：讓報告能說出「這是誰發布的、驗證到什麼程度」。
    # 同一個 repo 可能被多個 server 引用，取驗證最強的那個。
    meta = {}
    for slug in core + picked + domain_picked:
        reg = found.get(slug)
        if not reg:
            meta[slug] = {"registered": False}
            continue
        kind, label = namespace_kind(reg)
        prev = meta.get(slug)
        if prev and NS_RANK[prev["kind"]] <= NS_RANK[kind]:
            continue
        meta[slug] = {"registered": True, "name": reg,
                      "kind": kind, "label": label}
    META.write_text(json.dumps(
        {"synced_at": when, "registry_total": len(found), "servers": meta},
        ensure_ascii=False, indent=1), encoding="utf-8")

    by_kind = collections.Counter(
        v.get("label", "未登錄 registry") for v in meta.values())
    print("\n發布者身分分佈（本次名單）：")
    for k, c in by_kind.most_common():
        print(f"  {k:<18} {c:>3}")

    total = len(core) + len(picked) + len(domain_picked)
    if picked:
        lo = stats[picked[-1]]["stargazerCount"]
        hi = stats[picked[0]]["stargazerCount"]
        print(f"\n已寫出 {OUT.name}：{total} 個目標"
              f"（核心 {len(core)} + 同步 {len(picked)}，星數 {lo:,}–{hi:,}）")
    else:
        print(f"\n已寫出 {OUT.name}：{total} 個目標")
    print("接著執行：python batch.py targets.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
