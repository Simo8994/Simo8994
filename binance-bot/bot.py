#!/usr/bin/env python3
"""Bot spot Binance, trend-following adattivo. Va eseguito una volta al giorno (dopo le 00:05 UTC).

  python3 bot.py            esegue un ciclo (controlla i segnali e, se serve, piazza ordini)
  python3 bot.py --status   mostra lo stato senza fare nulla

Modalita' (config.json -> "mode"):
  dry      nessun ordine reale: simula gli eseguiti sul prezzo di chiusura (predefinita)
  testnet  ordini sulla testnet Binance (soldi finti)
  live     ordini reali
Chiavi API solo da variabili d'ambiente: BINANCE_API_KEY, BINANCE_API_SECRET.
"""
import hashlib, hmac, json, logging, os, sys, time, urllib.error, urllib.parse, urllib.request
from decimal import Decimal, ROUND_DOWN

from strategy import signal, select_params, vol_fraction, FEE

HERE = os.path.dirname(os.path.abspath(__file__))
URLS = {"live": "https://api.binance.com", "testnet": "https://testnet.binance.vision",
        "dry": "https://data-api.binance.vision"}
DEFAULTS = {"mode": "dry", "symbols": ["BTCUSDT", "ETHUSDT"], "capital": 400.0, "adaptive": True,
            "target_vol": 0.5, "max_drawdown": 0.5, "reselect_days": 30, "lookback": 730,
            "fixed_params": [20, 10]}
log = logging.getLogger("bot")


class ApiError(Exception):
    pass


class Client:
    def __init__(self, mode, key=None, secret=None, base_url=None):
        self.mode, self.key, self.secret = mode, key, secret
        self.base = base_url or URLS[mode]
        self.offset = 0

    def _http(self, method, url, headers):
        req = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            raise ApiError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:300]}") from None

    def public(self, path, **params):
        return self._http("GET", f"{self.base}{path}?{urllib.parse.urlencode(params)}", {})

    def signed(self, method, path, **params):
        if not (self.key and self.secret):
            raise ApiError("chiavi API mancanti (BINANCE_API_KEY / BINANCE_API_SECRET)")
        params.update(timestamp=int(time.time() * 1000) + self.offset, recvWindow=10000)
        q = urllib.parse.urlencode(params)
        sig = hmac.new(self.secret.encode(), q.encode(), hashlib.sha256).hexdigest()
        return self._http(method, f"{self.base}{path}?{q}&signature={sig}", {"X-MBX-APIKEY": self.key})

    def sync_time(self):
        self.offset = self.public("/api/v3/time")["serverTime"] - int(time.time() * 1000)

    def klines(self, symbol, limit=1000):
        d = self.public("/api/v3/klines", symbol=symbol, interval="1d", limit=limit)
        now = time.time() * 1000 + self.offset
        return [x for x in d if x[6] < now]  # solo candele chiuse

    def filters(self, symbol):
        info = self.public("/api/v3/exchangeInfo", symbol=symbol)["symbols"][0]
        f = {x["filterType"]: x for x in info["filters"]}
        notional = f.get("NOTIONAL") or f.get("MIN_NOTIONAL") or {}
        return {"base": info["baseAsset"], "quote": info["quoteAsset"], "step": Decimal(f["LOT_SIZE"]["stepSize"]),
                "min_qty": Decimal(f["LOT_SIZE"]["minQty"]),
                "min_notional": float(notional.get("minNotional", 10))}

    def free_balance(self, asset):
        for b in self.signed("GET", "/api/v3/account", omitZeroBalances="true")["balances"]:
            if b["asset"] == asset:
                return float(b["free"])
        return 0.0

    def market_order(self, symbol, side, client_id, **amount):
        """Ordine a mercato. Se la risposta si perde per un errore di rete, recupera l'ordine dal suo id."""
        try:
            return self.signed("POST", "/api/v3/order", symbol=symbol, side=side, type="MARKET",
                               newClientOrderId=client_id, newOrderRespType="FULL", **amount)
        except ApiError:
            raise
        except Exception as e:
            log.warning("risposta ordine persa (%s), verifico lo stato dell'ordine", e)
            time.sleep(3)
            return self.signed("GET", "/api/v3/order", symbol=symbol, origClientOrderId=client_id)


def floor_step(qty, step):
    return (Decimal(str(qty)) / step).to_integral_value(rounding=ROUND_DOWN) * step


def load_json(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save_state(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, path)


def new_state(cfg):
    per = cfg["capital"] / len(cfg["symbols"])
    return {"peak_equity": cfg["capital"], "halted": False,
            "symbols": {s: {"cash": per, "qty": 0.0, "spent": 0.0, "last_candle": 0,
                            "params": None, "params_candle": 0} for s in cfg["symbols"]}}


def buy(client, cfg, sym, st, price, candle, spend):
    flt = client.filters(sym)
    if spend < flt["min_notional"] * 1.05:
        log.warning("%s: importo %.2f sotto il minimo di Binance (%.2f), nessun acquisto", sym, spend, flt["min_notional"])
        return
    if cfg["mode"] == "dry":
        qty, cost = spend * (1 - FEE) / price, spend
    else:
        o = client.market_order(sym, "BUY", f"bot-{sym}-{candle}-B", quoteOrderQty=f"{spend:.2f}")
        if o.get("status") != "FILLED":
            raise ApiError(f"{sym}: acquisto non eseguito: {o}")
        qty, cost = float(o["executedQty"]), float(o["cummulativeQuoteQty"])
        qty -= sum(float(f["commission"]) for f in o.get("fills", []) if f["commissionAsset"] == flt["base"])
    st["qty"], st["spent"], st["cash"] = qty, cost, st["cash"] - cost
    log.info("%s: ACQUISTO %.8f a ~%.2f (speso %.2f)", sym, qty, cost / qty if qty else price, cost)


def sell(client, cfg, sym, st, price, candle, reason):
    flt = client.filters(sym)
    if cfg["mode"] == "dry":
        got = st["qty"] * price * (1 - FEE)
    else:
        qty = floor_step(min(st["qty"], client.free_balance(flt["base"])), flt["step"])
        if qty < flt["min_qty"] or float(qty) * price < flt["min_notional"]:
            log.warning("%s: quantita' %s troppo piccola per vendere, azzero la posizione nello stato", sym, qty)
            got = 0.0
        else:
            o = client.market_order(sym, "SELL", f"bot-{sym}-{candle}-S", quantity=format(qty, "f"))
            if o.get("status") != "FILLED":
                raise ApiError(f"{sym}: vendita non eseguita: {o}")
            got = float(o["cummulativeQuoteQty"])
            got -= sum(float(f["commission"]) for f in o.get("fills", []) if f["commissionAsset"] == flt["quote"])
    log.info("%s: VENDITA (%s), incassato %.2f, risultato %+.1f%%", sym, reason, got,
             (got / st["spent"] - 1) * 100 if st["spent"] else 0)
    st["cash"], st["qty"], st["spent"] = st["cash"] + got, 0.0, 0.0


def cycle(client, cfg, state, state_path):
    if cfg["mode"] != "dry":
        client.sync_time()
    data = {}
    for sym in cfg["symbols"]:
        k = client.klines(sym)
        if len(k) < 300:
            raise ApiError(f"{sym}: storico insufficiente ({len(k)} candele)")
        data[sym] = (k, [float(x[4]) for x in k], [float(x[2]) for x in k], [float(x[3]) for x in k])

    # interruttore di sicurezza: perdita massima sul capitale
    equity = sum(st["cash"] + st["qty"] * data[s][1][-1] for s, st in state["symbols"].items())
    state["peak_equity"] = max(state["peak_equity"], equity)
    log.info("capitale gestito: %.2f (massimo %.2f)", equity, state["peak_equity"])
    if not state["halted"] and equity < state["peak_equity"] * (1 - cfg["max_drawdown"]):
        log.error("PERDITA MASSIMA SUPERATA: vendo tutto e mi fermo")
        state["halted"] = True
        save_state(state_path, state)
    if state["halted"]:
        for sym, st in state["symbols"].items():
            if st["qty"] > 0:
                sell(client, cfg, sym, st, data[sym][1][-1], data[sym][0][-1][0], "stop generale")
                save_state(state_path, state)
        log.error("bot fermo: per ripartire rimuovi state.json dopo aver valutato la situazione")
        return

    for sym in cfg["symbols"]:
        k, c, h, l = data[sym]
        st = state["symbols"][sym]
        i, candle = len(c) - 1, k[-1][0]
        if candle <= st["last_candle"]:
            log.info("%s: candela gia' elaborata, niente da fare", sym)
            continue
        in_pos = st["qty"] > 0
        if not in_pos and (st["params"] is None or (candle - st["params_candle"]) >= cfg["reselect_days"] * 86400000):
            new = list(select_params(c, h, l, i - 1, cfg["lookback"])) if cfg["adaptive"] else list(cfg["fixed_params"])
            if new != st["params"]:
                log.info("%s: parametri %s -> %s", sym, st["params"], new)
            st["params"], st["params_candle"] = new, candle
        n_in, n_out = st["params"]
        # rielabora anche eventuali giorni saltati (massimo 30)
        first = max(i - 30, next((j for j in range(len(k)) if k[j][0] > st["last_candle"]), i)) if st["last_candle"] else i
        pos = in_pos
        for j in range(first, i + 1):
            s = signal(c, h, l, j, n_in, n_out, pos)
            pos = True if s == "enter" else False if s == "exit" else pos
        if pos and not in_pos:
            frac = vol_fraction(c, i, cfg["target_vol"])
            log.info("%s: segnale di ENTRATA, quota investita %.0f%%", sym, frac * 100)
            buy(client, cfg, sym, st, c[i], candle, st["cash"] * frac)
        elif in_pos and not pos:
            sell(client, cfg, sym, st, c[i], candle, "segnale di uscita")
        else:
            lvl = f"esce sotto {min(l[i + 1 - n_out:i + 1]):.2f}" if in_pos else \
                  f"entra sopra {max(max(h[i + 1 - n_in:i + 1]), sum(c[i - 99:i + 1]) / 100):.2f}"
            log.info("%s: chiusura %.2f, %s, nessuna azione (%s)", sym, c[i], "IN POSIZIONE" if in_pos else "fuori", lvl)
        st["last_candle"] = candle
        save_state(state_path, state)


def main(argv=None, client=None, base_dir=HERE):
    argv = sys.argv[1:] if argv is None else argv
    cfg = {**DEFAULTS, **load_json(os.path.join(base_dir, "config.json"), {})}
    if cfg["mode"] not in URLS:
        sys.exit(f"mode non valido: {cfg['mode']}")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join(base_dir, "bot.log"))])
    state_path = os.path.join(base_dir, f"state-{cfg['mode']}.json")
    state = load_json(state_path, None) or new_state(cfg)
    if "--status" in argv:
        print(json.dumps({"mode": cfg["mode"], **state}, indent=2))
        return 0
    client = client or Client(cfg["mode"], os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_API_SECRET"),
                              cfg.get("base_url"))
    log.info("--- ciclo in modalita' %s ---", cfg["mode"])
    try:
        cycle(client, cfg, state, state_path)
    except Exception as e:
        log.error("ciclo interrotto: %s", e)
        save_state(state_path, state)
        return 1
    save_state(state_path, state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
