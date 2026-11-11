"""Logica di strategia condivisa da bot e backtest (solo libreria standard).

Trend-following su candele giornaliere:
  entrata  = chiusura sopra il massimo degli ultimi n_in giorni E sopra la media a n_trend giorni
  uscita   = chiusura sotto il minimo degli ultimi n_out giorni
Adattamento:
  1. i parametri (n_in, n_out) vengono riscelti periodicamente tra poche combinazioni,
     in base al rendimento/rischio degli ultimi `lookback` giorni (walk-forward);
  2. la dimensione della posizione si riduce quando la volatilità è alta.
"""
import math

GRID = [(20, 10), (30, 15), (55, 20)]
N_TREND = 100
FEE = 0.001


def signal(c, h, l, i, n_in, n_out, in_pos, n_trend=N_TREND):
    """Decisione sulla candela chiusa i, usando solo dati fino a i. Ritorna 'enter', 'exit' o None."""
    if i < max(n_in, n_out, n_trend):
        return None
    if not in_pos:
        if c[i] > max(h[i - n_in:i]) and c[i] > sum(c[i - n_trend:i]) / n_trend:
            return "enter"
    elif c[i] < min(l[i - n_out:i]):
        return "exit"
    return None


def simulate(c, h, l, start, end, n_in, n_out, fee=FEE):
    """Simula parametri fissi sulle candele [start, end). Ritorna (equity finale, max drawdown)."""
    eq, pos, entry, peak, mdd = 1.0, False, 0.0, 1.0, 0.0
    for i in range(start, end):
        s = signal(c, h, l, i, n_in, n_out, pos)
        if s == "enter":
            pos, entry, eq = True, c[i], eq * (1 - fee)
        elif s == "exit":
            eq, pos = eq * c[i] / entry * (1 - fee), False
        e = eq * c[i] / entry if pos else eq
        peak = max(peak, e)
        mdd = max(mdd, 1 - e / peak)
    if pos:
        eq *= c[end - 1] / entry
    return eq, mdd


def select_params(c, h, l, i, lookback=730, grid=GRID, default=(20, 10)):
    """Sceglie la combinazione con il miglior rapporto rendimento/drawdown sugli ultimi `lookback` giorni fino a i incluso."""
    start = max(N_TREND, i + 1 - lookback)
    if i + 1 - start < 200:
        return default
    best, best_score = default, None
    for n_in, n_out in grid:
        eq, mdd = simulate(c, h, l, start, i + 1, n_in, n_out)
        score = (eq - 1) / max(mdd, 0.05)
        if best_score is None or score > best_score:
            best, best_score = (n_in, n_out), score
    return best


def vol_fraction(c, i, target_annual_vol=0.5, window=30):
    """Quota della dotazione da investire: 1 se la volatilità è <= target, meno se è più alta."""
    if not target_annual_vol or i < window:
        return 1.0
    r = [math.log(c[j] / c[j - 1]) for j in range(i - window + 1, i + 1)]
    m = sum(r) / len(r)
    vol = math.sqrt(sum((x - m) ** 2 for x in r) / (len(r) - 1)) * math.sqrt(365)
    return 1.0 if vol <= 0 else min(1.0, target_annual_vol / vol)
