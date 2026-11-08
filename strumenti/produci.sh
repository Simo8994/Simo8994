#!/usr/bin/env bash
# Produce tutte le storie: immagini mancanti, video IT (Nicola) e video EN (George).
# Uso: strumenti/produci.sh [cartelle...]   (default: tutte in video/)
# Variabili: PY_TTS (python con kokoro), PY_IMG (python con diffusers)
set -u
cd "$(dirname "$0")/.."
: "${PY_TTS:?serve PY_TTS}" "${PY_IMG:?serve PY_IMG}"
CARTELLE=("$@"); [ ${#CARTELLE[@]} -eq 0 ] && CARTELLE=(video/*/)
for d in "${CARTELLE[@]}"; do
  d=${d%/}; [ -f "$d/scene.json" ] || continue
  echo "=== $d $(date +%T)"
  "$PY_IMG" strumenti/genera_immagini.py "$d/scene.json" 2>&1 | grep -E '^\[|Nessuna|Error' || true
  python3 strumenti/crea_video.py "$d/scene.json" --kokoro im_nicola --python-tts "$PY_TTS" 2>&1 | grep -E 'Creato|Error|Traceback' || true
  python3 strumenti/crea_video.py "$d/scene.json" --kokoro bm_george --lingua en --python-tts "$PY_TTS" 2>&1 | grep -E 'Creato|Error|Traceback' || true
done
echo "=== FINE $(date +%T)"
