#!/usr/bin/env python3
"""Genera frasi con Kokoro TTS (gratuito, Apache 2.0).

    venv-tts/bin/python strumenti/voce_kokoro.py VOCE frasi.json cartella_out [velocita]

VOCE: im_nicola / if_sara (italiano), bm_george (inglese UK), am_onyx (inglese US) ...
La lingua si ricava dalla prima lettera della voce (i = italiano, a = US, b = UK).
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline


def main():
    voce, frasi_json, out_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    velocita = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    frasi = json.loads(frasi_json.read_text(encoding="utf-8"))
    pipe = KPipeline(lang_code=voce[0], repo_id="hexgrad/Kokoro-82M")
    for i, testo in enumerate(frasi):
        audio = np.concatenate([a for _, _, a in pipe(testo, voice=voce, speed=velocita)])
        sf.write(str(out_dir / f"frase_{i:02d}.wav"), audio, 24000)
        print(f"[{i + 1}/{len(frasi)}] {testo}", flush=True)


if __name__ == "__main__":
    main()
