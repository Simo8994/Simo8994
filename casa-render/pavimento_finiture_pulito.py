# Same method as pavimento_finiture.py, applied on the FLUX-cleaned photos,
# plus a matte pass: the low-frequency light hot-spot is flattened to the surrounding level.
import numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw, ImageFont
B = '/home/user/Simo8994/banana-output/parquet/'
FULL = [(0, 0), (1500, 0), (1500, 2000), (0, 2000)]
JOBS = [('cameretta', None, None),
        ('corridoio', [(615,525),(895,525),(1040,960),(1110,1000),(1150,1100),(1100,1630),(1240,1640),(1500,1660),(1500,2000),(0,2000),(0,1780),(330,1720),(440,1380),(575,640)], (392, 750, 120, 70)),
        ('soggiorno', [(0,600),(600,592),(690,512),(1120,500),(1500,1300),(1500,2000),(0,2000)], (425, 690, 110, 120))]
F = [('Pulito (prima della levigatura)', None),
     ('1. Faggio + vernice acqua opaca', ((228, 192, 152), 1.35)),
     ('2. Faggio naturale opaco (consigliato)', ((226, 204, 174), 1.32)),
     ('3. Faggio sbiancato sabbia opaco', ((232, 219, 198), 1.45))]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
gy, gx = np.mgrid[0:1000, 0:750]
for name, poly, glare in JOBS:
    src = Image.open(B + f'pulito_{name}.jpg').convert('RGB').resize((750, 1000), Image.LANCZOS)
    a = np.asarray(src).astype(float) / 255
    reg = Image.new('L', (750, 1000), 0); ImageDraw.Draw(reg).polygon([(x/2, y/2) for x, y in (poly or FULL)], fill=255)
    hsv = np.asarray(src.convert('HSV')).astype(float) / 255; h, s, v = hsv[...,0]*360, hsv[...,1], hsv[...,2]
    m = (h > 8) & (h < 48) & (s > .18) & (v > .15) & (np.asarray(reg) > 0)
    e = None
    if glare:
        cx, cy, rx, ry = glare; r = np.sqrt(((gx-cx)/rx)**2 + ((gy-cy)/ry)**2)
        e = np.clip(1.5 - r, 0, 1); m = m | ((e > 0) & (np.asarray(reg) > 0))
    m = np.asarray(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.5))).astype(float)[..., None] / 255
    Y = (a @ [.2126, .7152, .0722])[..., None] + 1e-4
    # matte: on the whole floor, divide out mid-scale light blobs (glare, hot-spots) and keep the
    # large-scale perspective falloff; floor-only normalized blur so walls don't leak in
    def mblur(x, w, r):
        f = lambda z: cv2.GaussianBlur(z.astype('float32'), (0, 0), r)
        return f(x * w) / (f(w) + 1e-4)
    fl = (m[..., 0] > .5).astype(float); y0 = Y[..., 0]
    fac = np.clip(mblur(y0, fl, 90) / (mblur(y0, fl, 18) + 1e-4), .62, 1.12)
    a = a * (1 + (fac[..., None] - 1) * m); Y = (a @ [.2126, .7152, .0722])[..., None] + 1e-4
    sel = m[..., 0] > .5; my = Y[sel].mean(); ratio = a / Y; dev = ratio / ratio[sel].mean(0) - 1
    g = Image.new('RGB', (1500, 2120), 'white'); d = ImageDraw.Draw(g)
    for i, (lab, p) in enumerate(F):
        if p:
            tint, k = p; tint = np.array(tint) / 255; ty = tint @ [.2126, .7152, .0722]
            Yn = (my + (Y - my) * .8) * k
            out = np.clip(tint / ty * Yn * (1 + .3 * dev), 0, 1)
            im = Image.fromarray(((a*(1-m) + out*m)*255).astype('uint8'))
        else: im = src
        x, y = (i % 2) * 750, (i // 2) * 1060
        d.text((x+16, y+14), lab, fill=(40,34,28), font=font); g.paste(im, (x, y+60))
    g.save(B + f'opaco_faggio_{name}.jpg', quality=90)
