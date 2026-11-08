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
PAUSA = 0.12          # silenzio tra le frasi (solo voce sintetica)
SR_MIX = 48000
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
          "sul", "sulla", "non", "si", "ci", "mi", "ti", "gli", "l'", "un'",
          "agli", "dal", "dalla", "dai", "dagli", "nei", "negli", "sui", "col", "suo",
          "sua", "suoi", "tua", "tuo", "mio", "mia", "più", "come", "se",
          # inglese
          "the", "a", "an", "of", "to", "in", "on", "at", "by", "for", "with", "and",
          "or", "but", "his", "her", "their", "your", "my", "is", "was", "it", "than"}


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
def genera_frasi_piper(frasi, modello, velocita, tmp):
    from piper import PiperVoice, SynthesisConfig
    voce = PiperVoice.load(modello)
    cfg = SynthesisConfig(length_scale=velocita)
    for n, parlato in enumerate(frasi):
        with wave.open(str(tmp / f"frase_{n:02d}.wav"), "wb") as wf:
            voce.synthesize_wav(parlato, wf, syn_config=cfg)


def genera_frasi_kokoro(frasi, voce, python_tts, tmp):
    lista = tmp / "frasi.json"
    lista.write_text(json.dumps(frasi, ensure_ascii=False), encoding="utf-8")
    run([python_tts, Path(__file__).parent / "voce_kokoro.py", voce, lista, tmp])


def genera_frasi_clonate(frasi, riferimento, python_tts, tmp):
    lista = tmp / "frasi.json"
    contenuto = json.dumps(frasi, ensure_ascii=False)
    # se le frasi sono identiche all'ultima volta, riusa l'audio gia' generato
    if lista.exists() and lista.read_text(encoding="utf-8") == contenuto and \
            all((tmp / f"frase_{n:02d}.wav").exists() for n in range(len(frasi))):
        print("Voce gia' generata: la riuso.")
        return
    lista.write_text(contenuto, encoding="utf-8")
    run([python_tts, Path(__file__).parent / "voce_clonata.py", riferimento, lista, tmp])


def voce_sintetica(dati, genera, tmp):
    frasi = [frase.get("voce", frase["testo"]) if isinstance(frase, dict) else frase
             for scena in dati["scene"] for frase in scena["frasi"]]
    genera(frasi)
    tempo = dati.get("tempo_voce", 1.0)  # >1 = voce piu' veloce
    # tutte le frasi allo stesso formato, poi silenzio tra una e l'altra
    silenzio = tmp / "silenzio.wav"
    run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
         "anullsrc=r=24000:cl=mono", "-t", PAUSA, silenzio])
    pezzi, inizi_scene, t, n = [], [], 0.0, 0
    for scena in dati["scene"]:
        inizi_scene.append(t)
        for _ in scena["frasi"]:
            wav = tmp / f"frase_{n:02d}_24k.wav"
            run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp / f"frase_{n:02d}.wav",
                 "-ar", "24000", "-ac", "1", "-af",
                 "silenceremove=start_periods=1:start_threshold=-50dB,"
                 "areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                 f"atempo={tempo}",
                 wav])
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


def tempi_whisper(voce_wav, prompt, lingua="it"):
    from faster_whisper import WhisperModel
    with wave.open(str(voce_wav)) as w:
        sr, ch = w.getframerate(), w.getnchannels()
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    a = a.reshape(-1, ch).mean(axis=1).astype(np.float32) / 32768
    if sr != 16000:  # ricampionamento semplice
        a = np.interp(np.arange(0, len(a), sr / 16000), np.arange(len(a)), a).astype(np.float32)
    modello = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = modello.transcribe(a, language=lingua, word_timestamps=True,
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
            debole = lambda k: copione[k][0].lower().strip(",.:;?!…") in DEBOLI
            if not fine and len(cur) > 1 and debole(cur[-1]) and p[-1] not in ",.:;?!":
                resto = []
                while len(cur) > 1 and debole(cur[-1]):  # sposta tutte le parole deboli finali
                    resto.insert(0, cur.pop())
                gruppi.append(cur)
                cur = resto
            else:
                gruppi.append(cur)
                cur = []
    if cur:
        gruppi.append(cur)
    return gruppi


def pulisci(p):
    return p.strip(",.;:").upper()


def scrivi_ass(copione, tempi, path, titolo=None, evidenzia=(), didascalie=()):
    ass = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "WrapStyle: 2", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Sub,{FONT},96,{BIANCO},{BIANCO},&H00000000&,&H99000000&,"
        "0,0,0,0,100,100,1,0,1,9,5,5,60,60,0,1",
        f"Style: Titolo,{FONT},210,{GIALLO},{GIALLO},&H00000000&,&H99000000&,"
        "0,0,0,0,100,100,2,0,1,12,7,5,40,40,0,1",
        f"Style: Sotto,{FONT},70,{BIANCO},{BIANCO},&H00000000&,&H99000000&,"
        "0,0,0,0,100,100,2,0,1,8,5,5,40,40,0,1",
        "Style: Didascalia,DejaVu Sans,34,&H00C0DCE8&,&H00C0DCE8&,&H00000000&,&H80000000&,"
        "-1,-1,0,0,100,100,3,0,1,3,2,5,40,40,0,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    if titolo:  # titolo d'impatto nei primi secondi, in alto
        fine_t = tempo_ass(titolo.get("durata", 2.6))
        pop = "\\fscx40\\fscy40\\t(0,120,\\fscx112\\fscy112)\\t(120,220,\\fscx100\\fscy100)"
        ass.append(f"Dialogue: 1,0:00:00.00,{fine_t},Titolo,,0,0,0,,"
                   f"{{\\pos({W // 2},{int(H * 0.22)}){pop}\\fad(0,150)}}{titolo['testo']}")
        if titolo.get("sotto"):
            ass.append(f"Dialogue: 1,0:00:00.15,{fine_t},Sotto,,0,0,0,,"
                       f"{{\\pos({W // 2},{int(H * 0.30)})\\fad(150,150)}}{titolo['sotto']}")
    for a, b, testo in didascalie:  # fonte/nome sotto la foto d'epoca
        ass.append(f"Dialogue: 1,{tempo_ass(a + 0.2)},{tempo_ass(b)},Didascalia,,0,0,0,,"
                   f"{{\\pos({W // 2},{int(H * 0.80)})\\fad(250,150)}}{testo}")
    evidenzia = {norm(e) for e in evidenzia}
    ROSSO = "&H003030FF&"   # BGR di #FF3030
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
                forte = norm(copione[kk][0]) in evidenzia or any(c.isdigit() for c in p)
                if kk == k:
                    colore, scala = (ROSSO, 130) if forte else (GIALLO, 115)
                    parti.append(f"{{\\c{colore}\\fscx{scala}\\fscy{scala}}}{p}"
                                 f"{{\\c{BIANCO}\\fscx100\\fscy100}}")
                elif forte:
                    parti.append(f"{{\\c{ROSSO}}}{p}{{\\c{BIANCO}}}")
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
    g.add_argument("--clona", help="campione della tua voce (wav) da clonare")
    g.add_argument("--kokoro", help="voce Kokoro, es. im_nicola, if_sara, bm_george")
    ap.add_argument("--python-tts", default="python3",
                    help="Python dell'ambiente con chatterbox-tts / kokoro")
    ap.add_argument("--velocita", type=float, default=0.9)
    ap.add_argument("--lingua", default="it", help="it oppure en (usa i campi *_en)")
    args = ap.parse_args()

    scene_path = Path(args.scene).resolve()
    base = scene_path.parent
    tmp = base / "_tmp"
    tmp.mkdir(exist_ok=True)
    dati = json.loads(scene_path.read_text(encoding="utf-8"))
    if args.lingua != "it":  # versione in un'altra lingua dallo stesso file
        L = args.lingua
        dati["lingua"] = L
        for chiave in ("titolo", "evidenzia", "output"):
            if f"{chiave}_{L}" in dati:
                dati[chiave] = dati[f"{chiave}_{L}"]
        for s in dati["scene"]:
            s["frasi"] = s[f"frasi_{L}"]
            if f"didascalia_{L}" in s:
                s["didascalia"] = s[f"didascalia_{L}"]
        tmp = base / f"_tmp_{L}"
        tmp.mkdir(exist_ok=True)

    if args.voce:
        voce_wav, inizi_scene = voce_sintetica(
            dati, lambda f: genera_frasi_piper(f, args.voce, args.velocita, tmp), tmp)
    elif args.clona:
        voce_wav, inizi_scene = voce_sintetica(
            dati, lambda f: genera_frasi_clonate(f, Path(args.clona).resolve(),
                                                 args.python_tts, tmp), tmp)
    elif args.kokoro:
        voce_wav, inizi_scene = voce_sintetica(
            dati, lambda f: genera_frasi_kokoro(f, args.kokoro, args.python_tts, tmp), tmp)
    else:
        voce_wav, inizi_scene = voce_registrata(Path(args.audio).resolve(), tmp), None
    durata = durata_wav(voce_wav)

    copione = parole_copione(dati)
    sentite = tempi_whisper(voce_wav, " ".join(p for p, _, _ in copione), dati.get("lingua", "it"))
    tempi = allinea(copione, sentite, durata)

    if inizi_scene is None:  # registrazione: la scena parte con la sua prima parola
        inizi_scene = [0.0]
        for i in range(1, len(dati["scene"])):
            k = next(k for k, c in enumerate(copione) if c[1] == i)
            inizi_scene.append(tempi[k][0] - 0.1)
    durate = [b - a for a, b in zip(inizi_scene, inizi_scene[1:] + [durata])]

    ass_path = tmp / "sottotitoli.ass"
    didascalie = [(a, a + d, s["didascalia"]) for a, d, s in
                  zip(inizi_scene, durate, dati["scene"]) if s.get("didascalia")]
    scrivi_ass(copione, tempi, ass_path, dati.get("titolo"), dati.get("evidenzia", []),
               didascalie)

    clip = []
    for i, (scena, d) in enumerate(zip(dati["scene"], durate)):
        frames = int(round(d * FPS))
        effetti = scena.get("effetti", [])
        # zoom piu' marcato, alternato dentro/fuori
        z = f"1+0.2*on/{frames}" if i % 2 == 0 else f"1.2-0.2*on/{frames}"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
        if "scossa" in effetti:  # tremolio di camera per ~0.7 s
            x += f"+if(lt(on,{int(FPS * 0.7)}),40*sin(on*2.7)*(1-on/{int(FPS * 0.7)}),0)"
            y += f"+if(lt(on,{int(FPS * 0.7)}),30*cos(on*3.1)*(1-on/{int(FPS * 0.7)}),0)"
            z = f"if(lt(on,{int(FPS * 0.7)}),1.1,{z})"
        ritaglio = ""
        if "ritaglio" in scena:  # [x, y, larghezza, altezza] in frazioni dell'immagine
            rx, ry, rw, rh = scena["ritaglio"]
            ritaglio = f"crop=iw*{rw}:ih*{rh}:iw*{rx}:ih*{ry},"
        vf = (f"{ritaglio}scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,"
              f"crop={W * 2}:{H * 2},"
              f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},setsar=1")
        if "flash" in effetti:
            vf += ",fade=in:st=0:d=0.35:color=white"
        sorgente = base / scena["immagine"]
        if scena.get("cornice"):  # foto d'epoca: intera al centro, sfondo sfocato
            sorgente = tmp / f"cornice_{i:02d}.png"
            run(["ffmpeg", "-loglevel", "error", "-y", "-i", base / scena["immagine"],
                 "-filter_complex",
                 f"[0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                 f"gblur=sigma=30,eq=brightness=-0.12[bg];"
                 f"[0]scale={W - 80}:{int(H * 0.62)}:force_original_aspect_ratio=decrease,"
                 f"pad=iw+12:ih+12:6:6:color=0xE8DCC0[fg];"
                 f"[bg][fg]overlay=(W-w)/2:(H-h)/2-{int(H * 0.06)}",
                 "-frames:v", "1", sorgente])
        out = tmp / f"clip_{i:02d}.mp4"
        run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", sorgente,
             "-vf", vf, "-frames:v", frames, "-c:v", "libx264", "-preset", "medium",
             "-crf", "18", "-pix_fmt", "yuv420p", out])
        clip.append(out)
    lista_v = tmp / "video.txt"
    lista_v.write_text("".join(f"file '{p}'\n" for p in clip))

    # effetti sonori: whoosh a ogni cambio scena, boato dove richiesto
    sfx_wav = tmp / "sfx.wav"
    scrivi_effetti(sfx_wav, durata, [
        (t, "boom" if "boom" in s.get("effetti", []) else "whoosh")
        for t, s in zip(inizi_scene, dati["scene"]) if t > 0 or "boom" in s.get("effetti", [])
    ])

    finale = base / dati.get("output", "video.mp4")
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
           "-i", lista_v, "-i", voce_wav, "-i", sfx_wav]
    # voce "da studio": calore, presenza, meno sibilanti, compressione
    mix = (f"[1:a]aresample={SR_MIX},highpass=f=70,equalizer=f=140:t=q:w=1:g=3,"
           "equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=7000:t=q:w=2:g=-2,"
           "acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,"
           "asplit=2[voce][chiave];"
           f"[2:a]volume={dati.get('volume_effetti', 0.5)}[sfx];")
    musica = dati.get("musica")
    if musica:
        inizio = musica.get("inizio", "auto")
        if inizio == "auto":
            inizio = punto_intenso(base / musica["file"], durata)
        cmd += ["-ss", str(inizio), "-i", base / musica["file"]]
        mix += (f"[3:a]aresample={SR_MIX},volume={musica.get('volume', 0.35)},"
                f"afade=t=in:d=0.5,afade=t=out:st={max(durata - 1.5, 0):.2f}:d=1.5[mus];"
                # la musica si abbassa quando parla la voce
                "[mus][chiave]sidechaincompress=threshold=0.04:ratio=6:attack=15:release=250[musd];"
                "[voce][musd][sfx]amix=inputs=3:normalize=0:duration=first,")
    else:
        mix += "[voce][sfx]amix=inputs=2:normalize=0:duration=first,"
    mix += "loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    # look cinematografico: contrasto, toni caldi/freddi, vignettatura, grana pellicola
    look = ("eq=contrast=1.08:saturation=1.08:gamma=0.97,"
            "colorbalance=rs=-0.04:bs=0.05:rh=0.06:bh=-0.05,"
            "vignette=angle=PI/4.5,noise=alls=4:allf=t,")
    cmd += ["-filter_complex",
            mix + f";[0:v]{look}subtitles={ass_path}:fontsdir={FONT_DIR}[v]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "6M",
            "-bufsize", "12M", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{durata:.2f}",
            finale]
    run(cmd)
    # anteprima leggera per guardarlo al volo dal telefono
    anteprima = finale.with_name(finale.stem + "-anteprima.mp4")
    run(["ffmpeg", "-loglevel", "error", "-y", "-i", finale, "-vf", "scale=540:960",
         "-c:v", "libx264", "-preset", "fast", "-crf", "28", "-c:a", "aac", "-b:a", "96k",
         "-movflags", "+faststart", anteprima])
    print(f"Creato: {finale} ({durata:.1f} s) + {anteprima.name}")


def punto_intenso(brano, durata):
    """Secondo d'inizio del tratto piu' energico del brano lungo quanto il video."""
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(brano), "-ac", "1",
                          "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
    a = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    energia = np.array([np.sqrt(np.mean(a[i:i + 8000] ** 2)) for i in range(0, len(a), 8000)])
    finestra = int(durata) + 1
    if len(energia) <= finestra:
        return 0
    somme = np.convolve(energia, np.ones(finestra), "valid")
    return int(np.argmax(somme[: len(energia) - finestra]))


# ---------------------------------------------------------------- effetti sonori
def _whoosh(sr):
    n = int(sr * 0.55)
    t = np.linspace(0, 1, n)
    rumore = np.random.default_rng(1).standard_normal(n)
    # filtro passa-basso con frequenza che sale e scende: effetto "passaggio"
    cut = 300 + 5000 * np.sin(np.pi * t) ** 2
    a = np.exp(-2 * np.pi * cut / sr)
    out = np.zeros(n)
    prev = 0.0
    for i in range(n):
        prev = (1 - a[i]) * rumore[i] + a[i] * prev
        out[i] = prev
    out *= np.sin(np.pi * t) ** 1.5
    return out / (np.abs(out).max() + 1e-9) * 0.7


def _boom(sr):
    n = int(sr * 1.8)
    t = np.arange(n) / sr
    freq = 38 + 50 * np.exp(-t * 6)
    basso = np.sin(2 * np.pi * np.cumsum(freq) / sr) * np.exp(-t * 2.2)
    rumore = np.random.default_rng(2).standard_normal(n) * np.exp(-t * 9)
    lp = np.zeros(n)
    prev = 0.0
    for i in range(n):  # rumore scuro, tipo esplosione
        prev = 0.06 * rumore[i] + 0.94 * prev
        lp[i] = prev
    lp /= np.abs(lp).max() + 1e-9
    out = np.tanh(2.5 * (basso + 0.8 * lp))
    return out / (np.abs(out).max() + 1e-9) * 0.95


def scrivi_effetti(path, durata, eventi):
    sr = SR_MIX
    traccia = np.zeros(int(sr * (durata + 2)))
    suoni = {"whoosh": _whoosh(sr), "boom": _boom(sr)}
    for t, tipo in eventi:
        s = suoni[tipo]
        i = max(int((t - (0.3 if tipo == "whoosh" else 0.02)) * sr), 0)
        traccia[i:i + len(s)] += s[:len(traccia) - i]
    traccia = np.clip(traccia[:int(sr * durata)], -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((traccia * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main()
