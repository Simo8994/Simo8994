# Render gratuito della casa

Render fotorealistico della casa con **Blender Cycles** (gratis, open source), senza servizi a pagamento.

## Requisiti
```
pip install bpy        # Blender come modulo Python (~400 MB)
```

## Uso
```
python3 render.py X,Y,Z,TX,TY,TZ FOV /percorso/assoluto/out.png [campioni] [larghezza] [altezza]
```
Coordinate in cm (X verso est, Y verso nord, Z altezza). Viste già usate:

| Vista | Comando |
|---|---|
| Cucina | `python3 render.py 320,190,175,70,480,110 62 $PWD/cucina.png 128 1600 1000` |
| Soggiorno / parete TV | `python3 render.py 60,115,125,360,230,112 58 $PWD/soggiorno.png 128 1600 1000` |
| Camera matrimoniale | `python3 render.py 735,190,160,380,400,80 70 $PWD/camera.png 128 1600 1000` |

Con 16 campioni e 640x400 si ottiene un'anteprima in ~15 s; 128 campioni a 1600x1000 richiedono ~6 min su 4 core.

## File
- `casa.json` – elenco degli oggetti (gruppo, nome, x0, y0, z0, x1, y1, z1 in cm)
- `casa_rows.txt` – stesso elenco in testo, usato anche dalla pianta
- `pianta.py` – genera la pianta dall'alto in SVG: `python3 pianta.py casa_rows.txt pianta.svg`
