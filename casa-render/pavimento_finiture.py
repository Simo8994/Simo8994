import numpy as np, sys
from PIL import Image, ImageFilter, ImageDraw, ImageFont
U = '/root/.claude/uploads/7fa817b1-3a28-5696-96e9-887cb2e33a1a/'
FULL = [(0, 0), (750, 0), (750, 1000), (0, 1000)]
JOBS = [('f0022d29-image.jpg', 'cameretta', None, None),
        ('5808c300-image.jpg', 'corridoio', [(615,525),(895,525),(1040,960),(1110,1000),(1150,1100),(1100,1630),(1240,1640),(1500,1660),(1500,2000),(0,2000),(0,1780),(330,1720),(440,1380),(575,640)], (392, 745, 80, 60)),
        ('96cc572c-image.jpg', 'soggiorno', [(0,600),(600,592),(690,512),(1120,500),(1500,1300),(1500,2000),(0,2000)], (430, 682, 80, 100))]
# chroma of the finish (applied on the photo's own light, which is kept) and how much the sanding lightens it
F = [('Com\'è ora (vernice vecchia ingiallita)', None),
     ('1. Faggio + vernice acqua trasparente', ((228, 192, 152), 1.35)),
     ('2. Faggio effetto naturale (fondo neutro)', ((226, 204, 174), 1.32)),
     ('3. Faggio sbiancato sabbia', ((232, 219, 198), 1.45))]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
for fn, name, poly, glare in JOBS:
    big = Image.open(U + fn).convert('RGB'); sx, sy = 750 / big.width, 1000 / big.height
    src = big.resize((750, 1000)); a = np.asarray(src).astype(float) / 255
    reg = Image.new('L', (750, 1000), 0); ImageDraw.Draw(reg).polygon([(x*sx, y*sy) for x, y in poly] if poly else FULL, fill=255)
    hsv = np.asarray(src.convert('HSV')).astype(float) / 255; h, s, v = hsv[...,0]*360, hsv[...,1], hsv[...,2]
    m = (h > 8) & (h < 48) & (s > .22) & (v > .15) & ~((v > .8) & (s < .4)) & (np.asarray(reg) > 0)
    m = np.asarray(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.5))).astype(float)[..., None] / 255
    if glare:  # light reflection on the varnish: treat it as floor too, or it leaves a halo
        gy, gx = np.mgrid[0:1000, 0:750]; cx, cy, rx, ry = glare
        e = np.clip(1.6 - np.sqrt(((gx - cx) / rx) ** 2 + ((gy - cy) / ry) ** 2), 0, 1)[..., None]; m = np.maximum(m, e)
    Y = (a @ [.2126, .7152, .0722])[..., None] + 1e-4; sel = m[..., 0] > .5
    my = Y[sel].mean(); ratio = a / Y; dev = ratio / ratio[sel].mean(0) - 1
    g = Image.new('RGB', (1500, 2120), 'white'); d = ImageDraw.Draw(g)
    for i, (lab, p) in enumerate(F):
        if p:
            tint, k = p; tint = np.array(tint) / 255; ty = tint @ [.2126, .7152, .0722]
            Yn = (my + (Y - my) * .8) * k  # sanding evens out the patina and removes the darkened varnish
            out = np.clip(tint / ty * Yn * (1 + .3 * dev), 0, 1)
            im = Image.fromarray(((a*(1-m) + out*m)*255).astype('uint8'))
        else: im = src
        x, y = (i % 2) * 750, (i // 2) * 1060
        d.text((x+16, y+14), lab, fill=(40,34,28), font=font); g.paste(im, (x, y+60))
    g.save(f'/home/user/Simo8994/banana-output/parquet/parquet_faggio_{name}.jpg', quality=90)
