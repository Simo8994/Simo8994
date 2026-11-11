"""Test senza rete: python3 -m unittest -v"""
import json, os, tempfile, unittest
from decimal import Decimal

import bot
from strategy import signal, select_params, vol_fraction

DAY = 86400000


def candles(closes):
    return [[j * DAY, str(p), str(p * 1.01), str(p * 0.99), str(p), "1", j * DAY + DAY - 1] for j, p in enumerate(closes)]


class FakeClient:
    """Imita Binance: registra gli ordini e risponde come l'API reale."""
    def __init__(self, series):
        self.series, self.orders, self.balances = series, [], {}

    def sync_time(self): pass
    def klines(self, symbol, limit=1000): return candles(self.series[symbol])
    def filters(self, symbol):
        return {"base": symbol[:-4], "quote": "USDT", "step": Decimal("0.00001"), "min_qty": Decimal("0.00001"), "min_notional": 5.0}
    def free_balance(self, asset): return self.balances.get(asset, 0.0)

    def market_order(self, symbol, side, client_id, **amount):
        self.orders.append((symbol, side, client_id, amount))
        price, base = self.series[symbol][-1], symbol[:-4]
        if side == "BUY":
            quote = float(amount["quoteOrderQty"]); qty = quote / price
            self.balances[base] = self.balances.get(base, 0) + qty * 0.999
            return {"status": "FILLED", "executedQty": str(qty), "cummulativeQuoteQty": str(quote),
                    "fills": [{"commission": str(qty * 0.001), "commissionAsset": base}]}
        qty = float(amount["quantity"]); self.balances[base] -= qty
        return {"status": "FILLED", "executedQty": str(qty), "cummulativeQuoteQty": str(qty * price),
                "fills": [{"commission": str(qty * price * 0.001), "commissionAsset": "USDT"}]}


FLAT = [100.0 + (j % 7) * 0.3 for j in range(400)]
UP = FLAT + [102 + 2 * j for j in range(1, 31)]            # rottura al rialzo
DOWN = UP + [UP[-1] - 6 * j for j in range(1, 6)]         # poi inversione


class StrategyTest(unittest.TestCase):
    def test_no_lookahead(self):
        c = UP[:]; h = [x * 1.01 for x in c]; l = [x * 0.99 for x in c]
        i = 405
        before = (signal(c, h, l, i, 20, 10, False), select_params(c, h, l, i), vol_fraction(c, i))
        for j in range(i + 1, len(c)):
            c[j] = h[j] = l[j] = 1.0
        self.assertEqual(before, (signal(c, h, l, i, 20, 10, False), select_params(c, h, l, i), vol_fraction(c, i)))

    def test_enter_and_exit(self):
        c = DOWN; h = [x * 1.01 for x in c]; l = [x * 0.99 for x in c]
        self.assertIsNone(signal(c, h, l, 399, 20, 10, False))
        self.assertEqual(signal(c, h, l, 401, 20, 10, False), "enter")
        self.assertEqual(signal(c, h, l, len(c) - 1, 20, 10, True), "exit")

    def test_vol_fraction_bounds(self):
        calm = [100 + 0.01 * j for j in range(60)]
        wild = [100 * (1.2 if j % 2 else 0.9) for j in range(60)]
        self.assertEqual(vol_fraction(calm, 59), 1.0)
        self.assertTrue(0 < vol_fraction(wild, 59) < 0.3)

    def test_floor_step(self):
        self.assertEqual(bot.floor_step(0.123456789, Decimal("0.00001")), Decimal("0.12345"))


class BotTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def run_bot(self, mode, series, **cfg):
        json.dump({"mode": mode, "symbols": ["BTCUSDT"], "capital": 200, "adaptive": False, "target_vol": None, **cfg},
                  open(os.path.join(self.dir, "config.json"), "w"))
        fc = FakeClient({"BTCUSDT": series})
        fc.balances = getattr(self, "balances", {})
        rc = bot.main([], client=fc, base_dir=self.dir)
        self.balances = fc.balances
        st = json.load(open(os.path.join(self.dir, f"state-{mode}.json")))
        return rc, fc, st

    def test_live_buy_then_sell(self):
        rc, fc, st = self.run_bot("live", FLAT)
        self.assertEqual((rc, fc.orders), (0, []))
        rc, fc, st = self.run_bot("live", UP[:402])
        self.assertEqual([o[1] for o in fc.orders], ["BUY"])
        s = st["symbols"]["BTCUSDT"]
        self.assertAlmostEqual(s["cash"], 0.0); self.assertAlmostEqual(s["spent"], 200.0)
        self.assertAlmostEqual(s["qty"], 200 / UP[401] * 0.999)       # commissione in BTC sottratta
        rc, fc, st = self.run_bot("live", UP[:402])                  # stesso giorno: nessun doppio ordine
        self.assertEqual(fc.orders, [])
        rc, fc, st = self.run_bot("live", DOWN)
        self.assertEqual([o[1] for o in fc.orders], ["SELL"])
        s = st["symbols"]["BTCUSDT"]
        self.assertEqual(s["qty"], 0.0); self.assertGreater(s["cash"], 200)   # venduto in guadagno
        self.assertLessEqual(float(fc.orders[0][3]["quantity"]), 200 / UP[401] * 0.999)

    def test_missed_days_still_exit(self):
        self.run_bot("dry", UP[:402])
        rc, fc, st = self.run_bot("dry", DOWN + [DOWN[-1] + 1])     # giorno dell'uscita saltato
        self.assertEqual(st["symbols"]["BTCUSDT"]["qty"], 0.0)

    def test_kill_switch(self):
        self.run_bot("live", UP[:402])
        crash = UP[:402] + [UP[401] * 0.4]
        rc, fc, st = self.run_bot("live", crash)
        self.assertTrue(st["halted"]); self.assertEqual([o[1] for o in fc.orders], ["SELL"])
        rc, fc, st = self.run_bot("live", crash + [500.0])          # resta fermo anche se il prezzo risale
        self.assertEqual(fc.orders, [])

    def test_below_min_notional_no_order(self):
        rc, fc, st = self.run_bot("live", UP[:402], capital=4)
        self.assertEqual(fc.orders, [])

    def test_order_error_keeps_state(self):
        json.dump({"mode": "live", "symbols": ["BTCUSDT"], "capital": 200, "adaptive": False, "target_vol": None},
                  open(os.path.join(self.dir, "config.json"), "w"))
        fc = FakeClient({"BTCUSDT": UP[:402]})
        def boom(*a, **k): raise bot.ApiError("HTTP 400")
        fc.market_order = boom
        self.assertEqual(bot.main([], client=fc, base_dir=self.dir), 1)
        st = json.load(open(os.path.join(self.dir, "state-live.json")))["symbols"]["BTCUSDT"]
        self.assertEqual((st["qty"], st["cash"], st["last_candle"]), (0.0, 200.0, 0))   # riprovera' al prossimo avvio


if __name__ == "__main__":
    unittest.main()
