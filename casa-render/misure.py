"""Adatta il modello (casa.json) alle misure reali prese col laser (cm, interni):
1 soggiorno-cucina 427 (al passaggio) x 574   2 ingresso 239 x 167   3 matrimoniale 408 x 398
4 bagno lavanderia 288 x 216   5 corridoio 99 x 489   6 cameretta 380 x 337   7 rientranza 100 x 97   8 bagno grande 267 x 199
Le pareti e i pavimenti vengono spostati sui nuovi fili; i mobili vengono traslati (non deformati)."""


def pl(pts):
    """piecewise-linear map through (old, new) breakpoints, constant shift outside"""
    def f(v):
        if v <= pts[0][0]: return v + pts[0][1] - pts[0][0]
        for (a, A), (b, B) in zip(pts, pts[1:]):
            if v <= b: return A + (v - a) * (B - A) / (b - a)
        return v + pts[-1][1] - pts[-1][0]
    return f


# zona giorno: cucina e soggiorno invariati (y >= 0); parete sud del soggiorno arretrata di 14 cm (574 cm); ingresso 167 cm
GX = pl([(0, 0), (432, 431), (445, 445)])
GY = pl([(-215, -192), (-202, -179), (-190, -167), (0, 0), (560, 560)])
# zona notte
EX = pl([(364, 364), (377, 377), (445, 445), (672, 733), (685, 746), (815, 785), (828, 798), (934, 934), (946, 947), (1204, 1214), (1217, 1227)])
EY = pl([(-185, -192), (-172, -179), (40, 37), (53, 50), (143, 149), (156, 162), (250, 249), (263, 262), (560, 560), (573, 573)])
STRETCH = ('Parete', 'Pavimento', 'Controparete', 'Terrazza', 'Marciapiede', 'Prato', 'Siepe', 'Area_Pranzo')
EAST_SOG = ('Parete_Est_Camera', 'Parete_Camera_Corridoio', 'Parete_Est_Ingresso_Porta_Corridoio')


def maps(g, n, x0, y0):
    if g == 'Zon' or n in EAST_SOG: return EX, EY
    if g == 'Gia': return EX if x0 > 900 else (lambda v: v), (lambda v: v)
    return GX, GY


def apply(rows):
    out = []
    for g, n, x0, y0, z0, x1, y1, z1 in rows:
        if n == 'Boiserie_Doghe_Noce': continue  # parete TV: solo muro bianco, niente listelli
        fx, fy = maps(g, n, x0, y0)
        if n.startswith(STRETCH):
            x0, x1, y0, y1 = fx(x0), fx(x1), fy(y0), fy(y1)
        else:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; dx, dy = fx(cx) - cx, fy(cy) - cy
            x0, x1, y0, y1 = x0 + dx, x1 + dx, y0 + dy, y1 + dy
        if n == 'Parete_Sud_Soggiorno': y0, y1 = -27, -14
        if n == 'Pavimento_Zona_Giorno': y0 = -14
        if n == 'Parete_Gradino_Portafinestra': y1 = -14
        if n == 'Pavimento_Passaggio_Corridoio': x1, y1 = 445, 149
        if n == 'Parete_Est_Ingresso_Porta_Corridoio': y0 = -192
        out.append([g, n, x0, y0, z0, x1, y1, z1])
    return out


def pt(x, y):
    """map a point (openings, lights): east of the entrance -> zona notte"""
    fx, fy = (EX, EY) if x >= 432 else (GX, GY)
    return fx(x), fy(y)


def opening(o):
    """OPEN row: x0, y0, x1, y1, sill, head"""
    x0, y0, x1, y1 = o[:4]
    cx, cy = pt((x0 + x1) / 2, (y0 + y1) / 2)
    hx, hy = (x1 - x0) / 2, (y1 - y0) / 2
    return [cx - hx, cy - hy, cx + hx, cy + hy, o[4], o[5]]
