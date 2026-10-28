"""Top-view plan (SVG) of the whole house + garden, from the SketchUp bbox dump (cm, Y north-up)."""
import math
import sys

rows = open(sys.argv[1]).read().split()
items = []
for r in rows:
    grp, name, nums = r.split("|")
    x0, y0, z0, x1, y1, z1 = map(float, nums.split(","))
    items.append((grp, name, x0, y0, z0, x1, y1, z1))

S = 0.62
PAD = 40
X0, X1, Y0, Y1 = -530, 1710, -330, 1030


def px(x, y):
    return PAD + (x - X0) * S, PAD + 40 + (Y1 - y) * S


def rect(x0, y0, x1, y1, fill, stroke="none", sw=0.6, op=1.0, rx=0):
    ax, ay = px(x0, y1)
    return (f'<rect x="{ax:.1f}" y="{ay:.1f}" width="{max(x1-x0,0.6)*S:.1f}" height="{max(y1-y0,0.6)*S:.1f}" rx="{rx}" '
            f'fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"/>')


def text(x, y, s, size=10, color="#222", weight="normal"):
    ax, ay = px(x, y)
    return (f'<text x="{ax:.1f}" y="{ay:.1f}" font-size="{size}" fill="{color}" text-anchor="middle" '
            f'font-family="Helvetica, Arial, sans-serif" font-weight="{weight}">{s}</text>')


def arc(hx, hy, r, a0, a1):
    p0 = px(hx + r * math.cos(math.radians(a0)), hy + r * math.sin(math.radians(a0)))
    p1 = px(hx + r * math.cos(math.radians(a1)), hy + r * math.sin(math.radians(a1)))
    h = px(hx, hy)
    sweep = 0 if a1 > a0 else 1
    return (f'<path d="M{h[0]:.1f},{h[1]:.1f} L{p0[0]:.1f},{p0[1]:.1f} A{r*S:.1f},{r*S:.1f} 0 0 {sweep} {p1[0]:.1f},{p1[1]:.1f}" '
            f'fill="none" stroke="#777" stroke-width="0.8" stroke-dasharray="3 2"/>')


COLORS = [("Sedia", "#f4f2ee"), ("Termoarredo", "#9aa3a8"), ("Divano", "#9a9a97"), ("Chaise", "#8c8c89"), ("Comodino", "#f4f2ee"), ("Testiera", "#f4f2ee"), ("Armadio_Matrimoniale", "#f4f2ee"), ("Matrimoniale_Letto", "#fbfaf6"), ("Colonna_Lavanderia", "#dfe6ea"), ("Ingresso_Bianc", "#fbfbf8"), ("Lettino_Neonato", "#f5f3ee"), ("Fasciatoio", "#f5f3ee"), ("Poltrona", "#e2c4ba"), ("Tappeto_Gioco", "#d6e2d0"), ("Libreria_Bassa", "#f5f3ee"), ("Armadio_L", "#f5f3ee"), ("Ascensore_Cabina", "#55575b"), ("Gradini", "#bdb8ad"), ("Pianerottolo", "#c9c4b8"), ("Pavimento_Vano", "#d9d5cc"), ("Controparete", "#f4f2ed"), ("Quadro", "#c0392b"), ("Prato", "#8fbf6a"), ("Siepe", "#3e6b3a"), ("Terrazza", "#d3cdbf"), ("Marciapiede", "#d3cdbf"),
          ("Vialetto", "#d3cdbf"), ("Area_Pranzo_Esterna", "#d3cdbf"), ("Pavimento_Bagno", "#c9c7c1"),
          ("Pavimento", "#e9dcc6"), ("LED", "#ffcf6e"), ("Vetro", "#8fb8cc"), ("Telaio", "#4a3a2e"),
          ("Porta_", "#f1efe9"), ("Parete_TV_Cartongesso", "#f4f2ed"), ("Parete", "#3b3b3b"),
          ("Penisola", "#3a3c3f"), ("Piano_Induzione", "#1d1d1f"), ("Cappa", "#1d1d1f"), ("Colonna", "#60422c"),
          ("Pensili", "#60422c"), ("Noce", "#60422c"), ("Mensola", "#60422c"), ("Boiserie", "#60422c"), ("Mobiletto", "#60422c"),
          ("Tavol", "#60422c"), ("Comodino", "#60422c"), ("Testiera", "#60422c"), ("Cassettiera", "#60422c"),
          ("Scrivania", "#60422c"), ("Mobile_Lavabo", "#60422c"), ("Sedia", "#3a3c3f"), ("Base", "#d6c8b2"),
          ("Top", "#efede8"), ("Zoccolo", "#3a3c3f"), ("Lavello", "#9aa3a8"), ("Divano", "#cdc8be"),
          ("Chaise", "#c4beb2"), ("Cuscin", "#96a58c"), ("Tappeto", "#b0a696"), ("Letto", "#e8e2d6"),
          ("Armadio", "#d6c8b2"), ("Scarpiera", "#d6c8b2"), ("Doccia", "#f4f4f2"), ("Lavabo", "#ffffff"),
          ("WC", "#ffffff"), ("Bidet", "#ffffff"), ("Lavatrice", "#ffffff"), ("TV", "#1d1d1f"), ("Lettino", "#96a58c"),
          ("Albero", "#4f8042")]


def color(name):
    for k, c in COLORS:
        if k in name:
            return c
    return "#bbbbbb"


SKIP = ("Cavo_", "Microonde", "Forno", "Specchio", "Schienale_", "Supporto", "Rubinetto", "Maniglie", "Telaio_Sopra",
        "Boiserie", "Gola")
el = []
ground = [i for i in items if any(k in i[1] for k in ("Prato", "Terrazza", "Marciapiede", "Vialetto", "Area_Pranzo_Esterna"))]
floors = [i for i in items if i[1].startswith("Pavimento")]
walls = [i for i in items if i[1].startswith("Parete") and "Cartongesso" not in i[1]]
trees = [i for i in items if i[1].startswith("Albero")]
rest = [i for i in items if i not in ground + floors + walls + trees and not any(k in i[1] for k in SKIP)]
el.append(rect(X0, Y0, X1, Y1, "#a9cf8a")); el.append(rect(-520, Y0, 685, -265, "#e6e3dd")); el.append(rect(685, Y0, X1, -3, "#e6e3dd"))
for i in ground + floors:
    el.append(rect(i[2], i[3], i[5], i[6], color(i[1])))
for i in sorted(rest, key=lambda r: r[7] if "Cappa" not in r[1] else 0):
    if "Cappa" in i[1]:
        el.append(rect(i[2], i[3], i[5], i[6], "none", stroke="#c9a227", sw=1))
        continue
    if "Rotondo" in i[1] or "Ovale" in i[1]:
        ax, ay = px((i[2] + i[5]) / 2, (i[3] + i[6]) / 2)
        el.append(f'<ellipse cx="{ax:.1f}" cy="{ay:.1f}" rx="{(i[5]-i[2])/2*S:.1f}" ry="{(i[6]-i[3])/2*S:.1f}" fill="#60422c" stroke="#2a1a10"/>')
        continue
    el.append(rect(i[2], i[3], i[5], i[6], color(i[1]), stroke="#00000040", sw=0.5,
                   rx=3 if any(k in i[1] for k in ("Divano", "Chaise", "Letto", "Sedia")) else 0))
for i in walls:
    el.append(rect(i[2], i[3], i[5], i[6], "#3b3b3b"))
# openings (x0,y0,x1,y1,orientation)
OPEN = [(-13, 294.5, 0, 394.5, "v"), (-13, 63, 0, 163, "v"), (224, 560, 324, 573, "h"), (179, -165, 192, -65, "v"),
        (450, 560, 550, 573, "h"), (640, 560, 740, 573, "h"), (845, 560, 945, 573, "h"), (1204, 100, 1217, 200, "v")]
for x0, y0, x1, y1, o in OPEN:
    el.append(rect(x0, y0, x1, y1, "#ffffff"))
    el.append(rect(x0 + 5, y0, x0 + 7.5, y1, "#5d8aa0") if o == "v" else rect(x0, y0 + 5, x1, y0 + 7.5, "#5d8aa0"))
DOORS = [(432, 50, 445, 130), (660, 143, 740, 156), (850, 250, 930, 263), (934, 63, 946, 143),
         (522, 40, 602, 53)]
for d in DOORS:
    el.append(rect(*d, "#e9dcc6"))
for a in [(444.7, 130, 80, 270, 360), (192, -65, 100, 270, 360), (740, 156, 80, 90, 180),
          (920, 155.7, 80, 180, 90), (946.5, 143, 80, 270, 360), (522, 40.3, 80, 270, 360), (224, 560, 100, 270, 360)]:
    el.append(arc(*a))
for i in trees:
    cx, cy = (i[2] + i[5]) / 2, (i[3] + i[6]) / 2
    ax, ay = px(cx, cy)
    el.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="{170*S:.1f}" fill="#4f8042" fill-opacity="0.85" stroke="#2f5a2a"/>')
PLANTS = []
for x, y in PLANTS:
    ax, ay = px(x, y)
    el.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="7" fill="#3f7d3a" stroke="#1f4a1c"/><circle cx="{ax:.1f}" cy="{ay:.1f}" r="3" fill="#7fb36a"/>')
LABELS = [(150, 430, "~26 m² (cucina+soggiorno+ingresso)"), (596, 420, "~18 m²"), (1000, 448, "~12-14 m²"), (1075, 117, "~5 m²"), (540, -118, "~4,5 m²"), (690, 78, "~4,5 m² · 5 quadri"), (150, 470, "CUCINA"), (262, 445, "tavolo Ø110"), (344, 505, "compl. 40"), (150, 230, "SOGGIORNO"), (290, -110, "INGRESSO"), (409, -140, "armadio"), (409, -45, "libreria"), (596, 470, "CAMERA"),
          (596, 440, "MATRIMONIALE"), (1000, 465, "CAMERETTA"), (1130, 300, "lettino"), (1080, 530, "armadio a L"), (690, 95, "CORRIDOIO"), (1075, 135, "BAGNO"),
          (540, -100, "BAGNO 2"), (642, 0, "lav.+asc."), (642, -20, "caldaia sopra"), (600, 800, "CORTE ESCLUSIVA – GIARDINO"), (600, 630, "terrazza"), (60, -170, "INGRESSO (portafinestra)"), (225, -35, "termo"),
          (250, 120, "passaggio libero →"), (300, -180, "cartongesso + termo"), (100, -290, "cancelletto"), (900, -150, "CONDOMINIO (escluso)")]
for x, y, s in LABELS:
    el.append(text(x, y, s, 11 if s.isupper() else 9, "#1a1a1a", "bold" if s.isupper() else "normal"))
W = PAD * 2 + (X1 - X0) * S
H = PAD * 2 + 80 + (Y1 - Y0) * S
bx, by = px(-480, -300); el.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{100*S:.1f}" height="6" fill="#222"/><rect x="{bx+100*S:.1f}" y="{by:.1f}" width="{100*S:.1f}" height="6" fill="#fff" stroke="#222"/><text x="{bx:.1f}" y="{by-5:.1f}" font-size="10" font-family="Helvetica">0</text><text x="{bx+100*S:.1f}" y="{by-5:.1f}" font-size="10" font-family="Helvetica">1 m</text><text x="{bx+200*S:.1f}" y="{by-5:.1f}" font-size="10" font-family="Helvetica">2 m</text>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}">'
       f'<rect width="{W:.0f}" height="{H:.0f}" fill="#fbfaf7"/>' + "".join(el) +
       f'<text x="{W/2:.0f}" y="28" font-size="17" font-family="Helvetica, Arial, sans-serif" font-weight="bold" '
       f'text-anchor="middle" fill="#222">Vista dall\'alto – casa completa e giardino</text>'
       f'<text x="{W/2:.0f}" y="{H-14:.0f}" font-size="10" font-family="Helvetica, Arial, sans-serif" text-anchor="middle" '
       f'fill="#555">Quote ricavate da planimetria (stato autorizzato) e misure fornite · H interna 270 cm · indicativo ±10 cm</text></svg>')
open(sys.argv[2], "w").write(svg)
print("ok", round(W), round(H))
