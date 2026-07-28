# -*- coding: utf-8 -*-
"""把思源黑體子集化成「只含本站標題用到的字」的顯示字體。

為什麼要這樣做：繁中字型檔動輒 5–10MB，整包載入不可能，這一直是本站與
premium 網站最明顯的質感差距。但首屏大標加上所有區塊標題其實只用到一百多
個字——把字型子集化到那一百多個字，檔案會落在幾十 KB，載入成本可以忽略。

這支腳本是**一次性建置工具**，產物 `assets/fonts/display.woff2` 直接進版控。
site.py 只負責複製，因此每日 CI 不需要 fonttools，也不會增加任何執行期相依。

用法：
    python make_font.py            # 需先有 site/index.html
    python make_font.py --src 路徑  # 指定思源黑體原始檔（可變字重 TTF）

字型授權：Noto Sans TC，SIL Open Font License 1.1（見 assets/fonts/OFL.txt）。
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "fonts"
SITE = ROOT / "site" / "index.html"

SRC_URL = ("https://raw.githubusercontent.com/google/fonts/main/ofl/"
           "notosanstc/NotoSansTC%5Bwght%5D.ttf")
OFL_URL = ("https://raw.githubusercontent.com/google/fonts/main/ofl/"
           "notosanstc/OFL.txt")

# 標題以外仍要保底的字：ASCII 可列印字元。專案名稱、數字、英文標題都吃得到，
# 而 latin 字形只佔幾 KB——為了避免「某個標題改字就缺字」，這個保險很划算。
BASE = "".join(chr(i) for i in range(0x20, 0x7F))
# 中文排版常用標點，同樣是缺一個就露餡的東西
PUNCT = "，。、；：？！「」『』（）《》〈〉—…·　～"

TAG_RE = re.compile(r"<[^>]+>")
HEAD_RE = re.compile(r"<h[123][^>]*>(.*?)</h[123]>", re.S | re.I)


def headline_chars(html: str) -> set[str]:
    """取出所有 h1/h2/h3 的可見文字字元。"""
    chars: set[str] = set()
    for raw in HEAD_RE.findall(html):
        text = TAG_RE.sub("", raw)
        text = text.replace("&nbsp;", " ").replace("&amp;", "&")
        chars.update(text)
    return {c for c in chars if c.strip()}


def fetch(url: str, dest: Path) -> Path:
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"下載 {url} …")
    with urllib.request.urlopen(url, timeout=300) as r, open(dest, "wb") as fh:
        fh.write(r.read())
    return dest


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser(description="產生子集化的標題顯示字體")
    ap.add_argument("--src", help="思源黑體可變字重 TTF；未指定則自動下載")
    args = ap.parse_args()

    try:
        from fontTools import subset
    except ImportError:
        print("需要 fonttools 與 brotli：pip install fonttools brotli", file=sys.stderr)
        return 2

    if not SITE.exists():
        print(f"找不到 {SITE}，請先執行 python site.py", file=sys.stderr)
        return 2

    chars = headline_chars(SITE.read_text(encoding="utf-8"))
    keep = "".join(sorted(chars | set(BASE) | set(PUNCT)))
    cjk = sum(1 for c in keep if ord(c) > 0x2E80)
    print(f"標題字元 {len(chars)} 個｜子集共 {len(keep)} 個（其中中日韓 {cjk} 個）")

    src = Path(args.src) if args.src else fetch(SRC_URL, OUT / "_NotoSansTC.ttf")
    fetch(OFL_URL, OUT / "OFL.txt")

    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / "display.woff2"

    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True
    opts.notdef_outline = False
    # 保留 wght 軸：一個檔案同時供 h1(800) 與 h2/h3(700) 使用，
    # 不必為每個字重各載一份。
    opts.retain_gids = False

    font = subset.load_font(str(src), opts)
    subsetter = subset.Subsetter(options=opts)
    subsetter.populate(text=keep)
    subsetter.subset(font)
    subset.save_font(font, str(dest), opts)
    font.close()

    kb = dest.stat().st_size / 1024
    print(f"已產生 {dest.relative_to(ROOT)}（{kb:.1f} KB）")
    if kb > 200:
        print("⚠ 檔案偏大，確認是否誤含了整套字符集", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
