# SwipeBills – prototipo

Chi ha una bolletta da pagare la carica; i benefattori scorrono le schede e con uno **swipe a destra** la pagano.

> Prototipo dimostrativo. Di default i pagamenti sono **simulati**; con Stripe si usano solo chiavi di **test**.

## Avvio

```bash
cd swipe-bills
npm install
npm run dev          # API su :3001, frontend su http://localhost:5173
```

Produzione locale: `npm run build && npm start` (serve tutto su :3001).
Test API: `npm test`.

### Variabili d'ambiente

| Variabile | Default | Note |
|---|---|---|
| `ADMIN_TOKEN` | `admin-dev` | Token della sezione *Verifica* |
| `STRIPE_SECRET_KEY` | – | Solo `sk_test_...`; se assente i pagamenti sono simulati |
| `BASE_URL` | `http://localhost:5173` | URL di ritorno da Stripe Checkout |
| `DATA_DIR` | `./data` | Archivio JSON e documenti caricati |
| `PORT` | `3001` | |

## Flusso

1. **Chiedi aiuto** – il richiedente carica il documento (PDF/JPG/PNG, max 5 MB) con fornitore, IBAN del fornitore, importo (1–5.000 €) e scadenza.
2. **Verifica** – l'amministratore controlla il documento e approva o rifiuta. Solo le bollette approvate entrano nel mazzo.
3. **Paga bollette** – swipe a sinistra = passa (memorizzato nel browser), swipe a destra = conferma e paga.
   Durante il checkout Stripe la bolletta resta riservata 30 minuti per evitare doppi pagamenti.
4. **Girata al fornitore** – l'admin segna l'avvenuto bonifico al fornitore.

## Scelte di sicurezza e privacy

- Documento, IBAN ed email **non sono mai esposti** dall'API pubblica; il documento è scaricabile solo con il token admin.
- I soldi vanno **al fornitore**, non al richiedente (riduce le frodi).
- IBAN validato con controllo mod-97.

## Cosa manca per una versione reale

- **Pagamento diretto al fornitore**: oggi l'incasso arriva sull'account Stripe della piattaforma e il bonifico al fornitore è manuale. Serve Stripe Connect / un PSP con payout verso terzi, o il pagamento via PagoPA/CBILL.
- **Quadro normativo**: custodire e girare fondi di terzi richiede una licenza di pagamento o l'appoggio a una piattaforma di donazioni autorizzata (PSD2, antiriciclaggio/KYC).
- **GDPR**: informativa, base giuridica, conservazione e cancellazione dei documenti; oscuramento automatico (OCR) se si vogliono mostrare le bollette.
- Autenticazione vera (utenti, benefattori, admin), database reale, webhook Stripe al posto della conferma al ritorno, antifrode sui documenti.
