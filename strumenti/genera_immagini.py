#!/usr/bin/env python3
"""Genera in locale (CPU) le immagini mancanti di un scene.json.

Ogni scena con "prompt" e un file "immagine" che non esiste ancora viene
generata con DreamShaper 8 + LCM (Stable Diffusion 1.5, licenza OpenRAIL-M,
uso commerciale consentito). ~1 minuto a immagine su 4 core.

    venv-img/bin/python strumenti/genera_immagini.py video/02-.../scene.json
"""
import json
import sys
from pathlib import Path

import torch
from diffusers import LCMScheduler, StableDiffusionPipeline

STILE = ", cinematic historical oil painting, dramatic lighting, masterpiece, highly detailed"
NEGATIVO = "text, letters, watermark, signature, blurry, deformed, extra limbs, modern objects"


def main():
    scene_path = Path(sys.argv[1]).resolve()
    base = scene_path.parent
    dati = json.loads(scene_path.read_text(encoding="utf-8"))
    da_fare = [s for s in dati["scene"]
               if s.get("prompt") and not (base / s["immagine"]).exists()]
    # piu' scene possono condividere la stessa immagine: generala una volta sola
    viste, lavori = set(), []
    for s in da_fare:
        if s["immagine"] not in viste:
            viste.add(s["immagine"])
            lavori.append(s)
    if not lavori:
        print("Nessuna immagine da generare.")
        return
    torch.set_num_threads(4)
    pipe = StableDiffusionPipeline.from_pretrained(
        "Lykon/dreamshaper-8", torch_dtype=torch.float32, safety_checker=None)
    pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
    pipe.load_lora_weights("latent-consistency/lcm-lora-sdv1-5")
    pipe.fuse_lora()
    for n, s in enumerate(lavori):
        out = base / s["immagine"]
        out.parent.mkdir(parents=True, exist_ok=True)
        img = pipe(s["prompt"] + STILE, negative_prompt=NEGATIVO, num_inference_steps=6,
                   guidance_scale=1.5, width=512, height=896,
                   generator=torch.Generator().manual_seed(s.get("seme", 7))).images[0]
        img.save(out)
        print(f"[{n + 1}/{len(lavori)}] {out.name}", flush=True)


if __name__ == "__main__":
    main()
