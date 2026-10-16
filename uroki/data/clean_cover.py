# python3 clean_cover.py <src> <dst> [alpha]  — рендер на сером/градиентном фоне -> 1200x900 на белом
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
def clean(src, dst, alpha=None):
    im = Image.open(src).convert('RGB')
    if alpha:
        a = Image.open(alpha).convert('L').resize(im.size)
        bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=a); im = bg
    w, h = im.size
    g = np.asarray(im.convert('L')).astype(np.int16)
    s = np.asarray(im.convert('HSV').split()[1]).astype(np.int16)
    m = ((g < 200) | (s > 60)).astype(np.uint8) * 255
    m[int(h * 0.9):, int(w * 0.8):] = 0
    mi = Image.fromarray(m).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(9))
    bb = mi.getbbox() or (0, 0, w, h)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    pad = int(0.09 * max(bw, bh))
    bb = (max(0, bb[0] - pad), max(0, bb[1] - pad), min(w, bb[2] + pad), min(h, bb[3] + pad))
    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2; bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    if bw / bh < 4 / 3: bw = bh * 4 / 3
    else: bh = bw * 3 / 4
    # если не влезает в исходник — добиваем белым полем
    canvas = Image.new('RGB', (int(max(w, bw)) + 2, int(max(h, bh)) + 2), 'white')
    ox, oy = (canvas.width - w) // 2, (canvas.height - h) // 2
    canvas.paste(im, (ox, oy)); cx += ox; cy += oy
    x0 = min(max(0, cx - bw / 2), canvas.width - bw); y0 = min(max(0, cy - bh / 2), canvas.height - bh)
    crop = canvas.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((1200, 900), Image.LANCZOS)
    a = np.asarray(crop).astype(np.float32)
    L = a.mean(2); sat = a.max(2) - a.min(2)
    t = np.clip((L - 195) / 40, 0, 1) * (sat < 16)
    a = a + (255 - a) * t[..., None]
    mk = Image.new('L', (1200, 900), 0); ImageDraw.Draw(mk).rectangle([55, 55, 1145, 845], fill=255)
    mk = np.asarray(mk.filter(ImageFilter.GaussianBlur(32))).astype(np.float32) / 255
    a = a * mk[..., None] + 255 * (1 - mk[..., None])
    Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(dst, quality=88, optimize=True, progressive=True)
if __name__ == '__main__':
    clean(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
