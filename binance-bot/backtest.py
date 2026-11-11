"""Backtest: confronta parametri fissi, parametri adattivi e adattivi + controllo volatilità.

Uso: python3 backtest.py [BTCUSDT ETHUSDT ...]
"""
import json, os, sys, time, urllib.request
from strategy import signal, select_params, vol_fraction, FEE, N_TREND

DATA_URL = "https://data-api.binance.vision"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def klines(sym, start_ms=1546300800000):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, sym + ".json")
    if os.path.exists(f) and time.time() - os.path.getmtime(f) < 3600:
        return json.load(open(f))
    out = []
    while True:
        u = f"{DATA_URL}/api/v3/klines?symbol={sym}&interval=1d&limit=1000&startTime={start_ms}"
        d = json.load(urllib.request.urlopen(u, timeout=30))
        out += d
        if len(d) < 1000:
            break
        start_ms = d[-1][0] + 86400000
        time.sleep(0.3)
    out = [x for x in out if x[6] < time.time() * 1000]  # solo candele chiuse
    json.dump(out, open(f, "w"))
    return out


def run(k, start, adaptive, target_vol, reselect_days=30, lookback=730, fixed=(20, 10)):
    c = [float(x[4]) for x in k]; h = [float(x[2]) for x in k]; l = [float(x[3]) for x in k]
    cash, qty, entry_val = 1.0, 0.0, 0.0
    params, peak, mdd, trades, curve = fixed, 1.0, 0.0, [], []
    for i in range(start, len(c)):
        if adaptive and qty == 0 and (i - start) % reselect_days == 0:
            params = select_params(c, h, l, i - 1, lookback)
        s = signal(c, h, l, i, params[0], params[1], qty > 0)
        if s == "enter":
            spend = (cash) * vol_fraction(c, i, target_vol)
            qty = spend * (1 - FEE) / c[i]; cash -= spend; entry_val = spend
        elif s == "exit":
            got = qty * c[i] * (1 - FEE)
            trades.append(got / entry_val - 1); cash += got; qty = 0.0
        e = cash + qty * c[i]
        peak = max(peak, e); mdd = max(mdd, 1 - e / peak); curve.append(e)
    return curve, mdd, trades


def stats(curve):
    peak, mdd = curve[0], 0.0
    for e in curve:
        peak = max(peak, e); mdd = max(mdd, 1 - e / peak)
    return curve[-1] / curve[0], mdd


def main():
    syms = sys.argv[1:] or ["BTCUSDT", "ETHUSDT"]
    data = {s: klines(s) for s in syms}
    n = min(len(k) for k in data.values())
    data = {s: k[-n:] for s, k in data.items()}
    variants = [("fissi 20/10", False, None), ("fissi + vol 50%", False, 0.5), ("adattivi", True, None), ("adattivi + vol 50%", True, 0.5)]
    # start dopo 830 giorni: cosi' la selezione adattiva ha sempre dati precedenti (nessuno sguardo al futuro)
    for label, start in [("da inizio test", N_TREND + 730), ("ultimi 3 anni", n - 1095), ("ultimo anno", n - 365)]:
        d0 = time.strftime("%Y-%m-%d", time.gmtime(data[syms[0]][start][0] / 1000))
        print(f"\n== {label} (dal {d0}) ==")
        port = {v[0]: None for v in variants}; bh_port = None
        for s in syms:
            k = data[s]; c = [float(x[4]) for x in k][start:]
            bh = [x / c[0] for x in c]; r, m = stats(bh)
            print(f"{s}: comprare e tenere x{r:.2f}, perdita max {m:.0%}")
            bh_port = bh if bh_port is None else [a + b for a, b in zip(bh_port, bh)]
            for name, ad, tv in variants:
                curve, mdd, tr = run(k, start, ad, tv)
                w = sum(1 for t in tr if t > 0)
                print(f"   {name:20s} x{curve[-1]:.2f}, perdita max {mdd:.0%}, {len(tr)} operazioni, vincenti {w / len(tr) if tr else 0:.0%}, peggiore {min(tr) if tr else 0:+.1%}")
                port[name] = curve if port[name] is None else [a + b for a, b in zip(port[name], curve)]
        r, m = stats(bh_port)
        print(f"PORTAFOGLIO (parti uguali): comprare e tenere x{r:.2f}, perdita max {m:.0%}")
        for name, curve in port.items():
            r, m = stats([1.0 * len(syms)] + curve)
            print(f"   {name:20s} x{r:.2f}, perdita max {m:.0%}")


if __name__ == "__main__":
    main()
