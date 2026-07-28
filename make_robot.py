# -*- coding: utf-8 -*-
"""首屏機器人素材的一次性處理:assets/robot/robot_a.png → assets/robot/robot.webp。

來源圖由 Higgsfield(nano_banana)生成,自帶一顆固定光球與掃描光束——
那兩樣必須拿掉:封包與光束由 canvas 動態繪製,才演得出「逐一評估」。

背景不是純黑而是帶深藍漸暈,所以不能塗黑(會留下黑斑),改用修補:
遮罩區域逐行取左右兩側的背景像素線性插值,再局部模糊融合。
左爪的發光點刻意保留——canvas 的動態掃描光束就從那裡發出。

輸出不去背:canvas 端用 screen 混合繪製,黑色像素不貢獻任何顏色,
等效透明——這正是整個首屏「加色混合、光是主體」的既有做法,
還避免了去背常見的白邊。

用法:python make_robot.py   (產物 assets/robot/robot.webp 進版控)
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "assets" / "robot" / "robot_a.png"
DST = ROOT / "assets" / "robot" / "robot.webp"

# 以下皆為 2048×2048 原圖座標(依預覽圖回推校正)。
ORB_C, ORB_R = (1554, 948), 205           # 光球:含光暈的整個範圍
CLAW_C, CLAW_R = (1543, 1085), 70         # 右爪:光暈遮罩必須繞開它
BEAM = ((895, 1222), (1620, 980))         # 光束(起點外保留左爪亮點)
BEAM_W = 80                               # 蓋到光束自己的光暈


def main() -> int:
    im = Image.open(SRC).convert("RGB")

    # 遮罩:光束線 + 光球圓,再挖掉爪尖保護圓
    mask = Image.new("L", im.size, 0)
    md = ImageDraw.Draw(mask)
    md.line([BEAM[0], BEAM[1]], fill=255, width=BEAM_W)
    cx, cy = ORB_C
    md.ellipse([cx - ORB_R, cy - ORB_R, cx + ORB_R, cy + ORB_R], fill=255)
    kx, ky = CLAW_C
    md.ellipse([kx - CLAW_R, ky - CLAW_R, kx + CLAW_R, ky + CLAW_R], fill=0)
    # 光球下緣的高光帶從爪指間穿過:保護圓之後再補一條窄橢圓,
    # 爪指最頂端會被削掉幾個像素,遠小於留下一條懸空亮帶的代價。
    md.ellipse([1474, 962, 1814, 1058], fill=255)

    # 逐行修補:遮罩區段用左右兩側的背景像素線性插值
    px, mk = im.load(), mask.load()
    W, H = im.size
    for y in range(H):
        x = 0
        while x < W:
            if mk[x, y]:
                xa = x
                while x < W and mk[x, y]:
                    x += 1
                xb = x - 1
                ca = px[max(0, xa - 3), y] if xa > 0 else px[min(W - 1, xb + 3), y]
                cb = px[min(W - 1, xb + 3), y] if xb < W - 1 else ca
                span = max(1, xb - xa)
                for i in range(xa, xb + 1):
                    t = (i - xa) / span
                    px[i, y] = tuple(round(ca[c] * (1 - t) + cb[c] * t)
                                     for c in range(3))
            x += 1

    # 融合:修補區域換成模糊版,抹掉插值的條紋痕
    blur = im.filter(ImageFilter.GaussianBlur(9))
    im.paste(blur, (0, 0), mask.filter(ImageFilter.GaussianBlur(3)))

    # 自動裁切:找出亮於背景的內容範圍,加留白後取方形
    gray = im.convert("L").point(lambda v: 255 if v > 26 else 0)
    bbox = gray.getbbox()
    if not bbox:
        print("找不到內容,來源圖有問題")
        return 1
    x0, y0, x1, y1 = bbox
    pad = 60
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(W, x1 + pad), min(H, y1 + pad)
    side = max(x1 - x0, y1 - y0)
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    bx = min(max(0, mx - side // 2), W - side)
    by = min(max(0, my - side // 2), H - side)
    im = im.crop((bx, by, bx + side, by + side))

    im = im.resize((900, 900), Image.LANCZOS)

    # 黑場校正 + 邊緣收光:canvas 端用 screen/lighter 混合,黑=透明。
    # 來源圖整片帶深藍漸暈、機身輝光又一路延伸到素材邊界——兩者都會
    # 讓方形邊界在深色背景上浮出來。三層處理:
    #   1. 暗於閾值的像素平滑壓向 0(漸暈歸零,本體與光暈保留)
    #   2. 邊緣 12% 線性壓黑(方形四邊)
    #   3. 徑向漸黑(輝光往邊界自然收攏,而不是被硬切)
    def smoothstep(t):
        t = 0.0 if t < 0 else 1.0 if t > 1 else t
        return t * t * (3 - 2 * t)

    px = im.load()
    n = im.width
    half = n / 2
    for y in range(n):
        for x in range(n):
            r, gc, b = px[x, y]
            v = max(r, gc, b)
            f = 1.0
            if v < 34:
                f = smoothstep((v - 8) / 26.0)
            e = min(x, n - 1 - x, y, n - 1 - y) / n
            f = min(f, smoothstep(e / 0.12))
            rad = ((x - half) ** 2 + (y - half) ** 2) ** 0.5 / half
            f = min(f, 1 - smoothstep((rad - 0.70) / 0.30))
            if f < 1.0:
                px[x, y] = (round(r * f), round(gc * f), round(b * f))

    DST.parent.mkdir(parents=True, exist_ok=True)
    im.save(DST, "WEBP", quality=88, method=6)
    print(f"{DST.relative_to(ROOT)}  {DST.stat().st_size / 1024:.0f} KB "
          f"(裁切 {side}px @ ({bx},{by}))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
