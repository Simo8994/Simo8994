---
name: interior-build
description: Trasforma una o più foto o render di una stanza in un breve video da interior designer (stile reel) con inquadrature cinematografiche, primi piani dei dettagli e movimenti di camera lenti. Usala quando l'utente scrive /interior-build, chiede un "video della stanza", un "walkthrough", un "reel" del progetto o di "animare" un render.
---

# /interior-build

Obiettivo: da un'immagine d'interni ottenere un video verticale (9:16, 1080x1920) di 10–25 secondi
che sembri girato da un videomaker d'interni: apertura larga, 3–5 dettagli (lampade, materiali,
porte, letto, top), chiusura larga. Tutto gratis, senza servizi a pagamento salvo approvazione.

## 1. Raccogli il materiale
- Immagini dell'utente (foto o render) oppure i render della casa in `banana-output/misure/`
  (`flux_*.jpg` fotorealistici, `stile_*.jpg` Blender).
- Se c'è un'immagine sola, va bene: le inquadrature di dettaglio si ricavano da quella.

## 2. Progetta le inquadrature (shot list)
Guarda l'immagine e scegli 4–7 inquadrature, alternando movimenti per non annoiare:
1. **Apertura**: tutta la stanza, `pan-right` o `pan-left`, 3,5 s.
2. **Dettagli**: 2–5 primi piani su ciò che rende bello l'ambiente (lampade a sospensione,
   venature del top, listelli, testiera, maniglie, tessuti, luce LED). Usa `focus`
   `[cx, cy, larghezza]` in frazioni dell'immagine (larghezza 0,25–0,45) con `zoom-in`,
   `tilt-down` (lampade, dall'alto verso il basso) o `pan-*`. 2,5–3 s ciascuno.
3. **Chiusura**: di nuovo larga con `zoom-out`, 3,5 s.

Salva la lista in `banana-output/interior-build/<nome>/shots.json`, formato descritto in
`scripts/walkthrough.py`.

## 3. (Opzionale) Dettagli più nitidi con l'AI
Un primo piano ricavato ritagliando l'immagine perde definizione. Se serve più qualità:
- **FLUX Kontext (gratis, poche immagini al giorno)**: `mcp__Ok__dynamic_space`, space
  `mcp-tools/FLUX.1-Kontext-Dev`, input = URL raw GitHub pubblico dell'immagine (con lo SHA del
  commit, per evitare la cache). Prompt: "Close-up detail shot of <dettaglio> from this exact room,
  same materials, colors and light, shallow depth of field, photorealistic interior photography".
- **Gemini (a pagamento)**: solo con la skill `banana` e approvazione esplicita dell'utente,
  dopo avergli detto il costo.
Usa le immagini ottenute come `img` delle inquadrature di dettaglio (`focus` non serve).

## 4. Monta il video
```
python3 .claude/skills/interior-build/scripts/walkthrough.py banana-output/interior-build/<nome>/shots.json banana-output/interior-build/<nome>/<nome>.mp4
```
`--format wide` per 16:9 (1920x1080). Il montaggio usa movimenti morbidi e dissolvenze di 0,7 s.

## 5. Controlla e consegna
- Estrai 3–4 fotogrammi (`ffmpeg -ss <t> -i video.mp4 -frames:v 1 f.jpg`) e guardali: niente
  bordi neri, dettagli riconoscibili, ritmo regolare.
- Invia il video con `SendUserFile` e una riga che elenca le inquadrature.
- I video stanno in `banana-output/` (non versionato): non committare foto private dell'utente.

## Regole
- Non inventare elementi che non ci sono nel progetto: i dettagli devono esistere nell'immagine
  di partenza (o nel render con le misure reali).
- Rispondi all'utente in italiano, breve.
