#!/usr/bin/env python3
"""Genera frasi parlate con la voce clonata (Chatterbox Multilingual).

Va eseguito con il Python dell'ambiente dove sono installati chatterbox-tts
e faster-whisper:
    venv-tts/bin/python strumenti/voce_clonata.py riferimento.wav frasi.json cartella_out

frasi.json: lista di stringhe. Output: cartella_out/frase_00.wav, frase_01.wav, ...

Per ogni frase genera fino a TENTATIVI versioni, le fa trascrivere a Whisper,
tiene quella piu' fedele al testo e taglia il rumore dopo l'ultima parola.
"""
import difflib
import json
import re
import sys
from pathlib import Path

import numpy as np
import torch
import torchaudio as ta
import torchaudio.functional as AF
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from faster_whisper import WhisperModel

TENTATIVI = 4
SOGLIA = 0.92  # somiglianza testo/trascrizione oltre cui ci si ferma subito
# (exaggeration, cfg_weight): espressivita' e aderenza al testo
IMPOSTAZIONI = [(0.3, 0.8), (0.25, 1.0), (0.4, 0.6), (0.3, 0.8)]


def parole(s):
    return re.sub(r"[^a-zàèéìòù0-9 ]", " ", s.lower()).split()


def main():
    ref, frasi_json, out_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    frasi = json.loads(frasi_json.read_text(encoding="utf-8"))
    torch.set_num_threads(4)
    modello = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    whisper = WhisperModel("small", device="cpu", compute_type="int8")

    for i, testo in enumerate(frasi):
        migliore = None
        for n in range(TENTATIVI):
            torch.manual_seed(1000 * i + n)
            ex, cfg = IMPOSTAZIONI[n % len(IMPOSTAZIONI)]
            wav = modello.generate(testo, language_id="it", audio_prompt_path=ref,
                                   exaggeration=ex, cfg_weight=cfg)
            a16 = AF.resample(wav, modello.sr, 16000)[0].numpy().astype(np.float32)
            segs = list(whisper.transcribe(a16, language="it", word_timestamps=True)[0])
            sentito = "".join(s.text for s in segs)
            voto = difflib.SequenceMatcher(None, parole(testo), parole(sentito)).ratio()
            fine = max((w.end for s in segs for w in s.words), default=wav.shape[-1] / modello.sr)
            if migliore is None or voto > migliore[0]:
                migliore = (voto, wav, fine, sentito)
            if voto >= SOGLIA:
                break
        voto, wav, fine, sentito = migliore
        taglio = min(wav.shape[-1], int((fine + 0.2) * modello.sr))
        wav = wav[:, :taglio]
        ta.save(str(out_dir / f"frase_{i:02d}.wav"), wav, modello.sr)
        print(f"[{i + 1}/{len(frasi)}] voto {voto:.2f} ({n + 1} tentativi) | {sentito.strip()}",
              flush=True)


if __name__ == "__main__":
    main()
