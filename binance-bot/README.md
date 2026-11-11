# Bot Binance spot – trend-following adattivo

Bot per BTC/USDT ed ETH/USDT su candele giornaliere. Solo libreria standard di Python 3 (nessuna installazione).

**Nessuna strategia garantisce profitti: puoi perdere denaro. Usa solo capitale che puoi permetterti di perdere.**

## Regole
- **Entrata:** la chiusura supera il massimo degli ultimi N giorni ed è sopra la media a 100 giorni.
- **Uscita:** la chiusura scende sotto il minimo degli ultimi M giorni.
- **Adattamento 1 – parametri:** ogni 30 giorni, quando è fuori dal mercato, il bot risceglie (N, M) tra 20/10, 30/15 e 55/20 in base al rapporto rendimento/perdita degli ultimi 2 anni.
- **Adattamento 2 – volatilità:** se la volatilità annua supera il 50%, investe solo una parte della dotazione.
- **Stop generale:** se il capitale gestito scende del 50% dal suo massimo, vende tutto e si ferma.

Il bot gestisce solo il budget indicato in `capital` (diviso in parti uguali tra i simboli), non l'intero conto.

## Uso
```bash
cp config.example.json config.json      # poi modifica capital e mode
python3 bot.py                          # un ciclo
python3 bot.py --status                 # stato attuale
python3 backtest.py                     # test sui dati storici
python3 -m unittest                     # test automatici
```

Modalità (`mode` in `config.json`):
| mode | cosa fa |
|---|---|
| `dry` | nessun ordine: simula gli eseguiti (predefinita, non servono chiavi) |
| `testnet` | ordini sulla testnet Binance, con chiavi create su testnet.binance.vision |
| `live` | ordini reali |

Chiavi API solo come variabili d'ambiente, mai nei file:
```bash
export BINANCE_API_KEY=...
export BINANCE_API_SECRET=...
```
Crea la chiave con **solo lettura + trading spot**, **prelievi disabilitati** e **restrizione IP**.

## Esecuzione giornaliera
Il bot va lanciato una volta al giorno dopo la chiusura della candela (00:00 UTC). Esempio con cron:
```
10 0 * * *  cd /percorso/binance-bot && BINANCE_API_KEY=... BINANCE_API_SECRET=... python3 bot.py
```
Rilanciarlo più volte nello stesso giorno non crea ordini doppi. Se salta qualche giorno, al riavvio recupera i segnali persi (fino a 30 giorni).

Deve girare da un Paese in cui Binance è disponibile: da località non ammesse l'API risponde con errore 451.

## File
- `strategy.py` – regole e adattamento (usato sia dal bot sia dal backtest)
- `bot.py` – esecuzione, ordini, stato, stop di sicurezza
- `backtest.py` – confronto storico tra varianti
- `state-<mode>.json`, `bot.log` – creati all'avvio; per ripartire dopo lo stop generale cancella il file di stato

## Percorso consigliato
1. `dry` per almeno 2-4 settimane, controllando `bot.log`.
2. `testnet` per verificare gli ordini con soldi finti.
3. `live` con una parte ridotta del capitale.
