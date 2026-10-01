# -*- coding: utf-8 -*-
"""產生離線備份包。

為什麼需要這支：GitHub 與 Vercel 是**運作**環境，不是**保險**。
倉庫被刪、帳號登不進去、合作夥伴誤 force-push——這幾種情況下
兩者會一起消失，因為 Vercel 部署的來源就是那個倉庫。
所以另外留一份能離線還原的副本。

刻意排除可重建的東西，因為備份的體積直接決定它多久被更新一次：

    site/              產物，site.py 0.3 秒重建
    reports/*.md       178 份個別報告，由 data.json 產生
    assets/og/*.jpg    分享預覽圖，make_og.py 可重做
                       （缺這個時 site.py 會正常跳過並提示,不會失敗）
    assets/robot/robot_a.png   4.4 MB 原始大圖,實際用的 robot.webp 有收

留下的是「能重建出一模一樣的網站」所需的最小集合，
以及 data.json——那是 178 個專案的真實掃描結果，
沒有 GitHub 存取與 11 分鐘的話重跑不出來，是唯一不可再生的資料。

用法：

    python3 make_backup.py            # 產生到 backup/
    python3 make_backup.py --verify   # 產生後解開重跑一次,確認真的能還原

`--verify` 不是可有可無的裝飾。沒有實際還原過的備份，
只是一個「看起來像備份的檔案」。
"""
from __future__ import annotations

import hashlib
import gzip
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "backup"

# 不進備份包的路徑（前綴比對，或以 / 結尾代表整個目錄）
SKIP = (
    "site/",
    "reports/",                    # data.json 另外壓,其餘 .md 可重建
    "assets/og/",
    "assets/robot/robot_a.png",
)


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT,
                         capture_output=True, check=True).stdout
    names = [n for n in out.decode("utf-8").split("\0") if n]
    return [n for n in names if not any(n.startswith(s) for s in SKIP)]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build() -> tuple[Path, Path, list[str]]:
    OUT.mkdir(exist_ok=True)
    files = tracked_files()

    src = OUT / "mcp-guard-source.tgz"
    with tarfile.open(src, "w:gz", compresslevel=9) as tar:
        for n in files:
            tar.add(ROOT / n, arcname=n)

    data = OUT / "data.json.gz"
    with (ROOT / "reports" / "data.json").open("rb") as fi, \
            gzip.open(data, "wb", compresslevel=9) as fo:
        shutil.copyfileobj(fi, fo)

    return src, data, files


def verify(src: Path, data: Path) -> bool:
    """解到暫存目錄重建網站並跑四套測試,與現有產物逐位元組比對。"""
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        with tarfile.open(src) as tar:
            tar.extractall(d)
        (d / "reports").mkdir(exist_ok=True)
        with gzip.open(data, "rb") as fi, (d / "reports" / "data.json").open("wb") as fo:
            shutil.copyfileobj(fi, fo)

        r = subprocess.run([sys.executable, "site.py"], cwd=d,
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("  ✗ site.py 失敗\n" + r.stderr[-600:])
            return False

        ok = True
        for name in ("index.html", "registry/index.html", "pick/index.html",
                     "method/index.html", "trust/index.html", "home.js"):
            a, b = ROOT / "site" / name, d / "site" / name
            if not b.exists() or a.read_bytes() != b.read_bytes():
                print(f"  ✗ 還原品與正式產物不一致：{name}")
                ok = False
        if ok:
            print("  ✅ 重建的網站與正式產物逐位元組相同")

        for t in ("test_poisoning", "test_lookup", "test_userinput", "test_routing"):
            r = subprocess.run([sys.executable, "-m", f"tests.{t}"], cwd=d,
                               capture_output=True, text=True)
            mark = "✅" if r.returncode == 0 else "❌"
            print(f"  {mark} tests.{t}")
            ok &= r.returncode == 0
        return ok


def main() -> int:
    src, data, files = build()
    print(f"備份包已產生到 {OUT}/")
    for p, what in ((src, f"原始碼與文件（{len(files)} 個檔案）"),
                    (data, "178 個專案的掃描結果")):
        print(f"  {p.name:<24} {p.stat().st_size / 1024:>6.0f} KB  "
              f"sha256:{sha256(p)[:16]}  {what}")

    if "--verify" not in sys.argv:
        print("\n加上 --verify 可以實際還原一次確認可用。")
        return 0

    print("\n── 還原驗證（解到暫存目錄重跑一次）──")
    if not verify(src, data):
        print("\n備份驗證未通過——不要當成可用的備份。")
        return 1
    print("\n備份可還原。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
