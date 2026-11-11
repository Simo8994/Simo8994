"""Photo composite of the TV wall on the client's real photo (riferimenti/parete_tv_foto.jpg, 1280x960).
The wall is almost fronto-parallel: scale ~3.35 px/cm on the wall plane, floor line y~800.
Elements: cleaned plaster, white skirting, walnut slat panel on black felt, 55" TV, floating console
(walnut fronts, matt black body) with LED, BTicino Living Now plates (sockets + thermostat), repaired parquet."""
import numpy as np, cv2, sys, os
BEIGE = os.environ.get('PARETE_BEIGE') == '1'  # dark beige matt lacquer for slats and console instead of walnut
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = 'casa-render/riferimenti/parete_tv_foto.jpg'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'banana-output/parete_tv/progetto_parete_tv.jpg'
S = 3.35                     # px per cm on the wall plane
FLOOR = 800                  # wall/floor line (y px)
WALL_R = 682                 # door frame starts here
VP = np.array([700., 500.])  # vanishing point (camera ~1 m high, looking slightly right)
D = 330.                     # camera distance from wall (cm), for depth projection
rng = np.random.default_rng(4)

img = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W = img.shape[:2]

def y_cm(h): return FLOOR - h * S          # height above floor -> y
def proj(x, y, d):                          # point on the wall plane pushed d cm towards the camera
    k = D / (D - d); return VP + (np.array([x, y]) - VP) * k

# ---------- 1. clean plaster ----------
wall = img[:FLOOR + 4, :WALL_R].copy()
g = cv2.cvtColor(wall.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
bg = cv2.GaussianBlur(g, (0, 0), 9)
m = (np.abs(g - bg) > 7).astype(np.uint8) * 255
for x0, y0, x1, y1 in ((520, 300, 682, 805), (80, 485, 125, 520), (0, 0, 40, 40)):  # boxes, wires, intercom, hole
    m[y0:y1, x0:x1] = 255
m[0:40, 0:40] = 0  # keep the window glare at the top-left corner
m = cv2.dilate(m, np.ones((5, 5), np.uint8))
clean = cv2.inpaint(wall.astype(np.uint8), m, 9, cv2.INPAINT_TELEA).astype(np.float32)
low = cv2.GaussianBlur(clean, (0, 0), 25)    # smooth light falloff of the room
# right strip (by the door) was full of boxes: rebuild it from the clean plaster profile of the same rows
prof = np.median(wall[:, 380:500], axis=1)                              # per-row plaster colour
prof = cv2.GaussianBlur(prof[:, None, :], (0, 0), 6)[:, 0, :]
ramp = np.linspace(1.0, 0.97, WALL_R - 500)[None, :, None]              # a touch darker towards the door reveal
ref = np.median(wall[90:280, 600:670].reshape(-1, 3), axis=0); cur = np.median(prof[90:280], axis=0)
low[:, 500:WALL_R] = prof[:, None, :] * ramp * (ref / cur)[None, None, :]
gr = low[:, 500:WALL_R].mean(axis=2, keepdims=True); low[:, 500:WALL_R] = 0.55 * low[:, 500:WALL_R] + 0.45 * gr * np.array([1.0, 0.995, 0.985]) * 1.04
fine = rng.normal(0, 1.2, low.shape[:2])[..., None]
wall_new = low + fine
wall_new[:40, :40] = wall[:40, :40]
img[:FLOOR + 4, :WALL_R] = wall_new

# ---------- 2. parquet repair (copy the intact parquet band, squeezed for perspective) ----------
src = img[884:958, 300:690].copy()                                     # clean parquet, rows closest to the gap
fill = np.zeros_like(img)
for y in range(796, 960):                                               # per-row resampling: rows get taller towards the camera
    t = (y - 796) / 164.0
    sy = int(np.clip(t * (src.shape[0] - 1), 0, src.shape[0] - 1))
    sc = 0.86 + 0.14 * t                                                  # horizontal scale grows towards the camera
    row = cv2.resize(src[sy:sy + 1], (int(src.shape[1] * sc), 1))[0]
    reps = int(np.ceil(720 / row.shape[0])) + 1
    fill[y, :720] = np.concatenate([row] * reps, axis=0)[:720]
mask_f = np.zeros((H, W), np.float32); mask_f[796:880, 0:640] = 1; mask_f[796:945, 0:250] = 1; mask_f[815:860, 570:640] = 1
mask_f = cv2.GaussianBlur(mask_f, (0, 0), 4)[..., None]
img = img * (1 - mask_f) + fill * mask_f

# ---------- helpers ----------
canvas = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
def blend(layer_rgba):
    global canvas
    canvas = Image.alpha_composite(canvas.convert('RGBA'), layer_rgba).convert('RGB')
def soft_shadow(poly, blur, alpha, offset=(0, 0)):
    L = Image.new('L', (W, H), 0); ImageDraw.Draw(L).polygon([(x + offset[0], y + offset[1]) for x, y in poly], fill=int(255 * alpha))
    L = L.filter(ImageFilter.GaussianBlur(blur))
    sh = Image.new('RGBA', (W, H), (20, 14, 10, 0)); sh.putalpha(L); blend(sh)
def glow(poly, blur, color, alpha):
    L = Image.new('L', (W, H), 0); ImageDraw.Draw(L).polygon(poly, fill=int(255 * alpha))
    L = L.filter(ImageFilter.GaussianBlur(blur))
    gl = Image.new('RGBA', (W, H), color + (0,)); gl.putalpha(L)
    global canvas
    base = np.asarray(canvas).astype(np.float32); a = np.asarray(L).astype(np.float32)[..., None] / 255
    canvas = Image.fromarray(np.clip(base + a * np.array(color, np.float32), 0, 255).astype(np.uint8))

def walnut(w, h, seed, vertical=True, base=(92, 60, 38)):
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    a = xx if vertical else yy; b = yy if vertical else xx
    grain = np.sin(a * 0.9 + 3 * np.sin(b * 0.013 + r.uniform(0, 6)) + r.uniform(0, 6)) * 0.5 + 0.5
    grain = cv2.GaussianBlur(grain, (0, 0), 0.7)
    sx, sy = (0.6, 6) if vertical else (6, 0.6)
    fib = cv2.GaussianBlur(r.normal(0, 1, (h, w)).astype(np.float32), (0, 0), sx, sigmaY=sy)
    v = (0.95 + 0.03 * grain + 0.02 * fib) if BEIGE else (0.82 + 0.16 * grain + 0.05 * fib)
    tone = r.uniform(0.93, 1.07)
    return np.clip(np.array(base, np.float32)[None, None] * v[..., None] * tone, 0, 255)

# ---------- 3. white skirting on the plain wall ----------
draw = ImageDraw.Draw(canvas)
PX0, PX1 = 0, int(290 + 85 * S)   # slat panel 170 cm wide, centred under the TV
sk_top = int(y_cm(7))
for x0, x1 in ((0, PX0), (PX1, WALL_R)):
    if x1 > x0:
        draw.rectangle([x0, sk_top, x1, FLOOR], fill=(236, 234, 229)); draw.line([x0, sk_top, x1, sk_top], fill=(205, 202, 196), width=1)

# ---------- 4. slat panel: 4 cm walnut slats, 1.6 cm gaps on black acoustic felt ----------
arr = np.asarray(canvas).astype(np.float32)
top = 0; bot = FLOOR
arr[top:bot, PX0:PX1] = np.array([58, 50, 43] if BEIGE else [22, 20, 19], np.float32)        # black felt
sw, gap = 4.0 * S, 1.6 * S
x = PX0 + 1; i = 0
while x + sw <= PX1:
    xa, xb = int(round(x)), int(round(x + sw))
    tex = walnut(xb - xa, bot - top, 100 + i, base=(150, 128, 102) if BEIGE else (92, 60, 38))
    shade = np.linspace(1.12, 0.86, xb - xa)[None, :, None]           # rounded light from the window (left)
    arr[top:bot, xa:xb] = tex * shade
    arr[top:bot, xb:min(xb + 2, PX1)] *= 0.55                           # cast shadow into the gap
    x += sw + gap; i += 1
# vertical light falloff (lighter at the top, like the plaster)
fall = np.linspace(1.05, 0.9, bot - top)[:, None, None]
arr[top:bot, PX0:PX1] *= fall
canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
soft_shadow([(PX1, 0), (PX1 + 6, 0), (PX1 + 6, FLOOR), (PX1, FLOOR)], 4, 0.35)   # panel edge shadow on plaster

# ---------- 5. 55" TV (123 x 71 x 2.5 cm), centre at 118 cm ----------
tw, th = 123 * S, 71 * S
cx, cy = 290, y_cm(118)
tv = [(cx - tw / 2, cy - th / 2), (cx + tw / 2, cy - th / 2), (cx + tw / 2, cy + th / 2), (cx - tw / 2, cy + th / 2)]
glow([(p[0], p[1]) for p in tv], 26, (255, 196, 128), 0.38)          # warm LED halo behind the TV
soft_shadow(tv, 10, 0.55, (6, 10))
front = [tuple(proj(px, py, 5)) for px, py in tv]
d = ImageDraw.Draw(canvas)
d.polygon(front, fill=(14, 14, 16))
fx0, fy0 = front[0]; fx1, fy1 = front[2]
d.rectangle([fx0 + 3, fy0 + 3, fx1 - 3, fy1 - 3], fill=(9, 10, 12))
# glossy reflection: soft diagonal band
refl = Image.new('L', (W, H), 0); rd = ImageDraw.Draw(refl)
rd.polygon([(fx0 + 40, fy0 + 3), (fx0 + 170, fy0 + 3), (fx0 + 60, fy1 - 3), (fx0 - 30, fy1 - 3)], fill=40)
refl = refl.filter(ImageFilter.GaussianBlur(18))
clip = Image.new('L', (W, H), 0); ImageDraw.Draw(clip).rectangle([fx0 + 3, fy0 + 3, fx1 - 3, fy1 - 3], fill=255)
refl = Image.fromarray((np.asarray(refl).astype(np.float32) * np.asarray(clip) / 255).astype(np.uint8))
wl = Image.new('RGBA', (W, H), (200, 210, 230, 0)); wl.putalpha(refl); blend(wl)
d = ImageDraw.Draw(canvas)
d.rectangle([(fx0 + fx1) / 2 - 10, fy1 - 2, (fx0 + fx1) / 2 + 10, fy1], fill=(60, 60, 64))  # logo strip

# ---------- 6. floating console 170 x 30 x 35 cm, bottom at 30 cm ----------
c0, c1 = PX0, PX1
cb, ct = y_cm(30), y_cm(60)
back = [(c0, ct), (c1, ct), (c1, cb), (c0, cb)]
fr = [tuple(proj(x, y, 35)) for x, y in back]
# LED under the console: warm wash on slats + floor
glow([(c0 + 10, cb), (c1 - 10, cb), (c1 - 10, cb + 2), (c0 + 10, cb + 2)], 14, (255, 170, 90), 0.9)
glow([(fr[3][0], fr[3][1] + 6), (fr[2][0], fr[2][1] + 6), (c1, FLOOR + 30), (c0, FLOOR + 30)], 22, (255, 160, 80), 0.35)
soft_shadow([(fr[3][0], FLOOR + 4), (fr[2][0], FLOOR + 4), (fr[2][0] + 10, FLOOR + 40), (fr[3][0] + 10, FLOOR + 40)], 16, 0.25)
d = ImageDraw.Draw(canvas)
# top face (seen from slightly above), side face, front
d.polygon([back[0], back[1], fr[1], fr[0]], fill=(168, 147, 120) if BEIGE else (40, 38, 37))
d.polygon([back[1], back[2], fr[2], fr[1]], fill=(112, 97, 79) if BEIGE else (26, 25, 25))
d.polygon(fr, fill=(128, 111, 90) if BEIGE else (30, 29, 29))
# walnut fronts: 3 push-to-open doors with 3 mm shadow gaps, 1.5 cm black frame
fx0, fy0 = fr[0]; fx1, fy1 = fr[2]
pad = 1.5 * S * D / (D - 35)
ix0, iy0, ix1, iy1 = max(0, int(fx0 + pad)), int(fy0 + pad), int(fx1 - pad), int(fy1 - pad)
arr = np.asarray(canvas).astype(np.float32)
wtex = walnut(ix1 - ix0, iy1 - iy0, 7, vertical=False, base=(146, 126, 101) if BEIGE else (104, 68, 42))
wtex *= np.linspace(1.08, 0.92, ix1 - ix0)[None, :, None]
arr[iy0:iy1, ix0:ix1] = wtex
for k in (1, 2):
    xs = int(ix0 + (ix1 - ix0) * k / 3); arr[iy0:iy1, xs - 1:xs + 1] = (70, 60, 50) if BEIGE else (18, 16, 15)
canvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(canvas)
d.line([fr[0], fr[1]], fill=(190, 170, 144) if BEIGE else (70, 66, 62), width=1)   # top edge highlight

# ---------- 7. BTicino Living Now plates (white) ----------
LN_W = (247, 246, 243); LN_B = (34, 33, 33)
def living_now(cx, cy, kind, color):
    """BTicino Living Now: full-cover flat keys, no visible frame. 5 pieces (end, 3 modules, end), 12 x 8.4 cm."""
    Q = 8; wcm, hcm = 12.0, 8.4
    tw, th = int(wcm * S * Q), int(hcm * S * Q)
    t = Image.new('RGBA', (tw, th), (0, 0, 0, 0)); dd = ImageDraw.Draw(t)
    base = LN_W if color == 'white' else LN_B
    seam = (196, 194, 189) if color == 'white' else (12, 12, 12)
    n = 5; pw = tw / n
    for k in range(n):
        x0, x1 = int(k * pw), int((k + 1) * pw)
        sh = 1.0 - 0.025 * k                                   # soft light from the left
        col = tuple(int(c * sh) for c in base)
        dd.rectangle([x0, 0, x1, th], fill=col + (255,))
        dd.line([x1 - 1, 0, x1 - 1, th], fill=seam + (255,), width=max(2, Q // 3))
    if kind == 'switch':
        for k in (1, 2, 3):
            mx = int((k + .5) * pw)
            dd.line([mx, int(th * .32), mx, int(th * .68)], fill=(178, 190, 214, 255), width=Q // 2)   # thin locator light
    elif kind == 'sockets':
        for k in (1, 2, 3):
            mx = int((k + .5) * pw); r = int(Q * 1.1)
            for yy in (.36, .5, .64):                          # bipasso / schuko-compatible holes
                cy0 = int(th * yy); dd.ellipse([mx - r, cy0 - r, mx + r, cy0 + r], fill=(120, 118, 114, 255))
    elif kind == 'thermo':                                     # 2-module display in the middle (modules 1-2)
        x0, x1 = int(1 * pw + Q), int(3 * pw - Q)
        dd.rectangle([x0, Q, x1, th - Q], fill=(10, 10, 11, 255))
        try: f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int(th * .30))
        except Exception: f = None
        dd.text(((x0 + x1) // 2 - int(th * .27), int(th * .30)), '20.5', fill=(236, 236, 236, 255), font=f)
        g = int(th * .10); dd.line([x0 + 3 * Q, th - 3 * Q, x0 + 3 * Q + g, th - 3 * Q], fill=(220, 220, 220, 255), width=Q // 2)
        px = x1 - 3 * Q - g // 2; dd.line([px - g // 2, th - 3 * Q, px + g // 2, th - 3 * Q], fill=(220, 220, 220, 255), width=Q // 2)
        dd.line([px, th - 3 * Q - g // 2, px, th - 3 * Q + g // 2], fill=(220, 220, 220, 255), width=Q // 2)
    small = t.resize((max(1, tw // Q), max(1, th // Q)), Image.LANCZOS)
    x0, y0 = int(cx - small.width / 2), int(cy - small.height / 2)
    soft_shadow([(x0, y0), (x0 + small.width, y0), (x0 + small.width, y0 + small.height), (x0, y0 + small.height)], 2.5, 0.45, (2, 3))
    global canvas
    c = canvas.convert('RGBA'); c.alpha_composite(small, (x0, y0)); canvas = c.convert('RGB')
LN_COL = os.environ.get('LN_COLOR', 'white')
living_now(631, 333, 'thermo', 'black')     # Living Now thermostat (black, as chosen) where the old one was, ~137 cm
living_now(631, 495, 'sockets', LN_COL)     # 3 Living Now sockets where the 3-module plate was, ~88 cm
living_now(631, 678, 'sockets', LN_COL)     # 3 sockets at ~35 cm instead of the open box
canvas = canvas.filter(ImageFilter.UnsharpMask(radius=1, percent=40, threshold=2))
canvas.save(OUT, quality=93)
print('saved', OUT)
