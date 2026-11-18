"""Monta un video "walkthrough" da interior designer partendo da una o più immagini.

Uso:
  python3 walkthrough.py shots.json out.mp4 [--format reel|wide] [--fps 30]

shots.json = lista di inquadrature, in ordine:
  [{"img": "cucina.jpg", "move": "pan-right", "sec": 3.5,
    "focus": [0.55, 0.45, 0.5]},     # centro x, centro y, larghezza (frazioni dell'immagine) - opzionale
   {"img": "camera.jpg", "move": "zoom-in", "sec": 3},
   ...]
move: pan-right | pan-left | zoom-in | zoom-out | tilt-up | tilt-down | still
Ogni inquadratura è un movimento lento e continuo; tra un'inquadratura e l'altra c'è una dissolvenza.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageOps

args = sys.argv[1:]
SHOTS = json.load(open(args[0])); OUT = args[1]
FMT = args[args.index('--format') + 1] if '--format' in args else 'reel'
FPS = int(args[args.index('--fps') + 1]) if '--fps' in args else 30
W, H = (1080, 1920) if FMT == 'reel' else (1920, 1080)
XF = 0.7  # durata dissolvenza (s)
TRAVEL = 0.18  # quanto si muove la camera (frazione del fotogramma)


def ease(t):  # movimento morbido: parte e arriva piano
    return t * t * (3 - 2 * t)


def frames_for(shot, d):
    im = ImageOps.exif_transpose(Image.open(shot['img'])).convert('RGB')
    iw, ih = im.size
    ar = W / H
    # finestra base con il rapporto del video, centrata sul fuoco richiesto
    fx, fy, fw = shot.get('focus', [0.5, 0.5, 1.0])
    bw = min(iw * fw, ih * ar); bh = bw / ar
    if bh > ih: bh = ih; bw = bh * ar
    cx, cy = fx * iw, fy * ih
    mv = shot.get('move', 'zoom-in'); n = int(round(d * FPS))
    for k in range(n):
        t = ease(k / max(n - 1, 1))
        z, dx, dy = 1.0, 0.0, 0.0
        if mv == 'zoom-in': z = 1 + TRAVEL * t
        elif mv == 'zoom-out': z = 1 + TRAVEL * (1 - t)
        elif mv == 'pan-right': z, dx = 1 + TRAVEL, (t - .5) * TRAVEL * bw
        elif mv == 'pan-left': z, dx = 1 + TRAVEL, (.5 - t) * TRAVEL * bw
        elif mv == 'tilt-up': z, dy = 1 + TRAVEL, (.5 - t) * TRAVEL * bh
        elif mv == 'tilt-down': z, dy = 1 + TRAVEL, (t - .5) * TRAVEL * bh
        w, h = bw / z, bh / z
        x0 = min(max(cx + dx - w / 2, 0), iw - w); y0 = min(max(cy + dy - h / 2, 0), ih - h)
        yield im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))


tmp = tempfile.mkdtemp(prefix='walk_')
clips = []
for i, s in enumerate(SHOTS):
    d = float(s.get('sec', 3.2)) + XF
    clip = os.path.join(tmp, f'c{i:02d}.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', clip], stdin=subprocess.PIPE)
    for fr in frames_for(s, d): p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); clips.append((clip, d))
    print('inquadratura', i + 1, '/', len(SHOTS))

# dissolvenze incrociate tra le inquadrature
cmd = ['ffmpeg', '-y', '-loglevel', 'error']
for c, _ in clips: cmd += ['-i', c]
if len(clips) == 1:
    fc, last = '[0:v]null[v]', '[v]'
else:
    parts, off, prev = [], 0.0, '[0:v]'
    for i in range(1, len(clips)):
        off += clips[i - 1][1] - XF
        lab = f'[x{i}]'
        parts.append(f'{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}{lab}')
        prev = lab
    fc, last = ';'.join(parts), prev
cmd += ['-filter_complex', fc, '-map', last, '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT]
subprocess.run(cmd, check=True)
print('video pronto:', OUT)
