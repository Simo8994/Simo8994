#!/usr/bin/env python3
"""Crea un video verticale (1080x1920) da un file JSON di scene.

Ogni scena: un'immagine + una o piu' frasi. Per ogni frase genera la voce
con Piper TTS, poi monta immagini con zoom lento, voce e sottotitoli.

Uso:
    python3 strumenti/crea_video.py video/01-guerra-piu-breve/scene.json \
        --voce /percorso/it_IT-paola-medium.onnx
"""
import argparse
import json
import subprocess
import wave
from pathlib import Path

from piper import PiperVoice, SynthesisConfig

W, H, FPS = 1080, 1920, 30
PAUSA = 0.25  # secondi di silenzio tra una frase e l'altra
PAROLE_PER_SOTTOTITOLO = 3


def run(cmd):
    subprocess.run(cmd, check=True)


def durata_wav(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def tempo_ass(t):
    h, rest = divmod(t, 3600)
    m, s = divmod(rest, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("--voce", required=True, help="modello Piper .onnx")
    ap.add_argument("--velocita", type=float, default=0.9,
                    help="length_scale Piper: <1 piu' veloce, >1 piu' lento")
    args = ap.parse_args()

    scene_path = Path(args.scene).resolve()
    base = scene_path.parent
    tmp = base / "_tmp"
    tmp.mkdir(exist_ok=True)
    dati = json.loads(scene_path.read_text(encoding="utf-8"))

    voce = PiperVoice.load(args.voce)
    cfg = SynthesisConfig(length_scale=args.velocita)

    # 1) voce: un wav per frase + silenzi, timeline dei sottotitoli
    silenzio = tmp / "silenzio.wav"
    rate = voce.config.sample_rate
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
         f"anullsrc=r={rate}:cl=mono", "-t", str(PAUSA), silenzio])

    pezzi_audio, sottotitoli, durate_scene = [], [], []
    t = 0.0
    n = 0
    for scena in dati["scene"]:
        inizio_scena = t
        for frase in scena["frasi"]:
            testo = frase["testo"] if isinstance(frase, dict) else frase
            parlato = frase.get("voce", testo) if isinstance(frase, dict) else frase
            wav = tmp / f"frase_{n:02d}.wav"
            with wave.open(str(wav), "wb") as wf:
                voce.synthesize_wav(parlato, wf, syn_config=cfg)
            d = durata_wav(wav)
            # sottotitoli a gruppi di parole, tempi proporzionali ai caratteri
            parole = testo.split()
            gruppi = [" ".join(parole[i:i + PAROLE_PER_SOTTOTITOLO])
                      for i in range(0, len(parole), PAROLE_PER_SOTTOTITOLO)]
            tot = sum(len(g) for g in gruppi)
            tt = t
            for g in gruppi:
                dg = d * len(g) / tot
                sottotitoli.append((tt, tt + dg, g))
                tt += dg
            pezzi_audio += [wav, silenzio]
            t += d + PAUSA
            n += 1
        durate_scene.append(t - inizio_scena)

    lista = tmp / "audio.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in pezzi_audio))
    voce_wav = tmp / "voce.wav"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", lista, voce_wav])

    # 2) file sottotitoli ASS
    ass = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Sub,DejaVu Sans,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,"
        "-1,0,0,0,100,100,0,0,1,7,3,2,80,80,620,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for a, b, g in sottotitoli:
        ass.append(f"Dialogue: 0,{tempo_ass(a)},{tempo_ass(b)},Sub,,0,0,0,,"
                   f"{{\\fad(60,0)}}{g.upper()}")
    ass_path = tmp / "sottotitoli.ass"
    ass_path.write_text("\n".join(ass) + "\n", encoding="utf-8")

    # 3) clip video per scena con zoom lento (alternato dentro/fuori)
    clip = []
    for i, (scena, d) in enumerate(zip(dati["scene"], durate_scene)):
        frames = int(round(d * FPS))
        img = base / scena["immagine"]
        if i % 2 == 0:
            z = f"1+0.12*on/{frames}"
        else:
            z = f"1.12-0.12*on/{frames}"
        out = tmp / f"clip_{i:02d}.mp4"
        vf = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,"
              f"crop={W * 2}:{H * 2},"
              f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"d={frames}:s={W}x{H}:fps={FPS},setsar=1")
        run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", img,
             "-vf", vf, "-frames:v", str(frames), "-c:v", "libx264",
             "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out])
        clip.append(out)

    lista_v = tmp / "video.txt"
    lista_v.write_text("".join(f"file '{p}'\n" for p in clip))

    # 4) montaggio finale: video + voce + sottotitoli
    finale = base / dati.get("output", "video.mp4")
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", lista_v, "-i", voce_wav,
         "-vf", f"subtitles={ass_path}",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-movflags", "+faststart", "-shortest", finale])
    print(f"Creato: {finale} ({t:.1f} s)")


if __name__ == "__main__":
    main()
