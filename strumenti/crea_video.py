#!/usr/bin/env python3
"""Crea un video verticale (1080x1920) da un file JSON di scene.

Ogni scena: un'immagine + una o piu' frasi. La voce puo' essere:
  - sintetica (Piper TTS):       --voce modello.onnx
  - la tua registrazione:        --audio narrazione.m4a
    (leggi le frasi di scene.json nell'ordine; i tempi li trova Whisper)

I sottotitoli sono sincronizzati parola per parola con Whisper e usano
l'effetto "karaoke": parola attiva evidenziata e ingrandita.

Esempi:
    python3 strumenti/crea_video.py video/01-guerra-piu-breve/scene.json --voce it_IT-paola-medium.onnx
    python3 strumenti/crea_video.py video/01-guerra-piu-breve/scene.json --audio mia_voce.m4a
"""
import argparse
import difflib
import json
import re
import subprocess
import unicodedata
import wave
from pathlib import Path

import numpy as np

W, H, FPS = 1080, 1920, 30
PAUSA = 0.25          # silenzio tra le frasi (solo voce sintetica)
MAX_PAROLE = 3        # parole per riga di sottotitolo
MAX_CARATTERI = 18
FONT_DIR = Path(__file__).parent / "font"
FONT = "Montserrat Black"
GIALLO = "&H0000D4FF&"   # BGR di #FFD400
BIANCO = "&H00FFFFFF&"
# parole corte che non devono restare in fondo a una riga
DEBOLI = {"il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "a", "da",
          "in", "con", "su", "per", "tra", "fra", "e", "o", "ma", "che", "del",
          "della", "dei", "delle", "al", "alla", "ai", "alle", "nel", "nella",
          "sul", "sulla", "non", "si", "ci", "mi", "ti", "gli", "l'", "un'"}


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True)


def durata_wav(path):
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def norm(p):
    p = unicodedata.normalize("NFKD", p.lower())
    p = "".join(c for c in p if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", p)


def tempo_ass(t):
    h, rest = divmod(max(t, 0), 3600)
    m, s = divmod(rest, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


# ---------------------------------------------------------------- voce
def voce_sintetica(dati, modello, velocita, tmp):
    from piper import PiperVoice, SynthesisConfig
    voce = PiperVoice.load(modello)
    cfg = SynthesisConfig(length_scale=velocita)
    silenzio = tmp / "silenzio.wav"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
         f"anullsrc=r={voce.config.sample_rate}:cl=mono", "-t", PAUSA, silenzio])
    pezzi, inizi_scene, t, n = [], [], 0.0, 0
    for scena in dati["scene"]:
        inizi_scene.append(t)
        for frase in scena["frasi"]:
            parlato = frase.get("voce", frase["testo"]) if isinstance(frase, dict) else frase
            wav = tmp / f"frase_{n:02d}.wav"
            with wave.open(str(wav), "wb") as wf:
                voce.synthesize_wav(parlato, wf, syn_config=cfg)
            pezzi += [wav, silenzio]
            t += durata_wav(wav) + PAUSA
            n += 1
    lista = tmp / "audio.txt"
    lista.write_text("".join(f"file '{p}'\n" for p in pezzi))
    out = tmp / "voce.wav"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", lista, out])
    return out, inizi_scene


def voce_registrata(audio, tmp):
    out = tmp / "voce.wav"
    # pulizia leggera: taglia rumori bassi, voce piu' presente
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", audio, "-ac", "1", "-ar", "48000",
         "-af", "highpass=f=80,afftdn=nf=-25,"
                "silenceremove=start_periods=1:start_threshold=-45dB", out])
    return out


# ---------------------------------------------------------------- tempi parole
def parole_copione(dati):
    """[(parola_da_mostrare, indice_scena, fine_frase)]"""
    out = []
    for i, scena in enumerate(dati["scene"]):
        for frase in scena["frasi"]:
            testo = frase["testo"] if isinstance(frase, dict) else frase
            parole = testo.split()
            for j, p in enumerate(parole):
                out.append((p, i, j == len(parole) - 1))
    return out


def tempi_whisper(voce_wav, prompt):
    from faster_whisper import WhisperModel
    with wave.open(str(voce_wav)) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    a = a.reshape(-1, ch).mean(axis=1).astype(np.float32) / 32768
    if sr != 16000:  # ricampionamento semplice
        a = np.interp(np.arange(0, len(a), sr / 16000), np.arange(len(a)), a).astype(np.float32)
    modello = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = modello.transcribe(a, language="it", word_timestamps=True,
                                 initial_prompt=prompt[:800])
    return [(w.word.strip(), w.start, w.end) for s in segs for w in s.words]


def allinea(copione, sentite, durata):
    """Assegna (inizio, fine) a ogni parola del copione."""
    a = [norm(p) for p, _, _ in copione]
    b = [norm(w) for w, _, _ in sentite]
    tempi = [None] * len(copione)
    for blocco in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blocco.size):
            _, s, e = sentite[blocco.b + k]
            tempi[blocco.a + k] = (s, e)
    # parole non riconosciute: distribuite tra le ancore vicine
    i = 0
    while i < len(tempi):
        if tempi[i] is not None:
            i += 1
            continue
        j = i
        while j < len(tempi) and tempi[j] is None:
            j += 1
        t0 = tempi[i - 1][1] if i > 0 else 0.0
        t1 = tempi[j][0] if j < len(tempi) else durata
        pesi = [max(len(copione[k][0]), 2) for k in range(i, j)]
        tot, t = sum(pesi), t0
        for k, p in zip(range(i, j), pesi):
            d = (t1 - t0) * p / tot
            tempi[k] = (t, t + d)
            t += d
        i = j
    return tempi


# ---------------------------------------------------------------- sottotitoli
def righe(copione, tempi):
    """Raggruppa le parole in righe corte, spezzando a fine frase/punteggiatura."""
    gruppi, cur = [], []
    for k, (p, _, fine) in enumerate(copione):
        cur.append(k)
        testo = " ".join(copione[i][0] for i in cur)
        stop = fine or p[-1] in ",.:;?!" or len(cur) >= MAX_PAROLE or len(testo) >= MAX_CARATTERI
        if stop:
            # non lasciare una parola debole in fondo alla riga
            if not fine and len(cur) > 1 and norm(copione[cur[-1]][0]) in DEBOLI \
                    and p[-1] not in ",.:;?!":
                ultimo = cur.pop()
                gruppi.append(cur)
                cur = [ultimo]
            else:
                gruppi.append(cur)
                cur = []
    if cur:
        gruppi.append(cur)
    return gruppi


def pulisci(p):
    return p.strip(",.;:").upper()


def scrivi_ass(copione, tempi, path):
    ass = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "WrapStyle: 2", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Sub,{FONT},96,{BIANCO},{BIANCO},&H00000000&,&H99000000&,"
        "0,0,0,0,100,100,1,0,1,9,5,5,60,60,0,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    pos = f"\\pos({W // 2},{int(H * 0.68)})"
    gruppi = righe(copione, tempi)
    for g_i, g in enumerate(gruppi):
        fine_riga = tempi[g[-1]][1]
        if g_i + 1 < len(gruppi):  # resta a schermo fino alla riga successiva
            fine_riga = max(fine_riga, tempi[gruppi[g_i + 1][0]][0])
        for idx, k in enumerate(g):
            inizio = tempi[k][0] if idx else tempi[k][0] - 0.05
            fine = tempi[g[idx + 1]][0] if idx + 1 < len(g) else fine_riga
            parti = []
            for kk in g:
                p = pulisci(copione[kk][0])
                if kk == k:
                    parti.append(f"{{\\c{GIALLO}\\fscx115\\fscy115}}{p}{{\\c{BIANCO}\\fscx100\\fscy100}}")
                else:
                    parti.append(p)
            effetto = pos
            if idx == 0:  # entrata "pop" della riga
                effetto += "\\fscx70\\fscy70\\t(0,90,\\fscx108\\fscy108)\\t(90,150,\\fscx100\\fscy100)"
            ass.append(f"Dialogue: 0,{tempo_ass(inizio)},{tempo_ass(fine)},Sub,,0,0,0,,"
                       f"{{{effetto}}}" + " ".join(parti))
    path.write_text("\n".join(ass) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--voce", help="modello Piper .onnx (voce sintetica)")
    g.add_argument("--audio", help="la tua registrazione del copione")
    ap.add_argument("--velocita", type=float, default=0.9)
    args = ap.parse_args()

    scene_path = Path(args.scene).resolve()
    base = scene_path.parent
    tmp = base / "_tmp"
    tmp.mkdir(exist_ok=True)
    dati = json.loads(scene_path.read_text(encoding="utf-8"))

    if args.voce:
        voce_wav, inizi_scene = voce_sintetica(dati, args.voce, args.velocita, tmp)
    else:
        voce_wav, inizi_scene = voce_registrata(Path(args.audio).resolve(), tmp), None
    durata = durata_wav(voce_wav)

    copione = parole_copione(dati)
    sentite = tempi_whisper(voce_wav, " ".join(p for p, _, _ in copione))
    tempi = allinea(copione, sentite, durata)

    if inizi_scene is None:  # registrazione: la scena parte con la sua prima parola
        inizi_scene = [0.0]
        for i in range(1, len(dati["scene"])):
            k = next(k for k, c in enumerate(copione) if c[1] == i)
            inizi_scene.append(tempi[k][0] - 0.1)
    durate = [b - a for a, b in zip(inizi_scene, inizi_scene[1:] + [durata])]

    ass_path = tmp / "sottotitoli.ass"
    scrivi_ass(copione, tempi, ass_path)

    clip = []
    for i, (scena, d) in enumerate(zip(dati["scene"], durate)):
        frames = int(round(d * FPS))
        z = f"1+0.12*on/{frames}" if i % 2 == 0 else f"1.12-0.12*on/{frames}"
        out = tmp / f"clip_{i:02d}.mp4"
        vf = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,"
              f"crop={W * 2}:{H * 2},"
              f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
              f"d={frames}:s={W}x{H}:fps={FPS},setsar=1")
        run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", base / scena["immagine"],
             "-vf", vf, "-frames:v", frames, "-c:v", "libx264", "-preset", "medium",
             "-crf", "18", "-pix_fmt", "yuv420p", out])
        clip.append(out)
    lista_v = tmp / "video.txt"
    lista_v.write_text("".join(f"file '{p}'\n" for p in clip))

    finale = base / dati.get("output", "video.mp4")
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
         "-i", lista_v, "-i", voce_wav,
         "-vf", f"subtitles={ass_path}:fontsdir={FONT_DIR}",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", finale])
    print(f"Creato: {finale} ({durata:.1f} s)")


if __name__ == "__main__":
    main()
