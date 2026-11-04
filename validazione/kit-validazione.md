# Kit di validazione: Cambio Ospite (nome provvisorio)

Obiettivo: in 14 giorni capire se i co-host hanno davvero il problema di pulizie e rendiconti e se pagherebbero circa 6 € per alloggio al mese. Riferimento: `ricerche/affitti-brevi-2026-11-04.md`.

## 1. Metti online la landing page (circa 20 minuti, gratis)

1. Crea un account gratuito su [Formspree](https://formspree.io): New form → copia l'indirizzo del modulo (tipo `https://formspree.io/f/abcdwxyz`).
2. Apri `validazione/landing/index.html` e incollalo in `const FORM_ENDPOINT = "";`.
3. Aggiungi in cima al file le righe di intestazione standard, prima di `<title>`:
   `<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">`
   Poi aggiungi in fondo al file `</html>`. Il browser le aggiunge comunque da solo, ma così la pagina è corretta.
4. Vai su [Netlify Drop](https://app.netlify.com/drop) e trascina la cartella `landing`. Ottieni subito un link pubblico.
5. Prima di pubblicare, scegli un nome definitivo e controllalo (marchi, dominio): "Cambio Ospite" è solo provvisorio. Posso farlo io con `/replica-brand`.

Se preferisci, posso farlo io su GitHub Pages: dimmelo.

## 2. Trova 10 persone da intervistare

Obiettivo: 6 co-host o gestori con 2-10 alloggi e 4 host privati.

Dove:
- **Rete co-host di Airbnb**: la pagina della tua zona elenca i co-host con il profilo (es. airbnb.com/host/<città>-italy/co-hosts). Contattali tramite il loro sito o i social.
- **Gruppi Facebook** per host e affitti brevi della tua città o regione.
- **Imprese di pulizia** che lavorano con gli affitti brevi: conoscono decine di host e soffrono lo stesso problema.
- **Conoscenti**: chiunque affitti su Airbnb, anche solo un alloggio.

### Messaggio WhatsApp o diretto
> Ciao [nome], ho visto che gestisci alloggi su Airbnb a [città]. Sto costruendo uno strumento per co-host che crea in automatico i turni di pulizia dai calendari e prepara il rendiconto mensile per i proprietari. Prima di andare avanti vorrei capire come lavori oggi: ti andrebbe una chiamata di 20 minuti questa settimana? Non vendo niente, mi serve solo il tuo parere.

### Post per gruppi Facebook
> Domanda per chi gestisce affitti brevi per conto di proprietari: come organizzate le pulizie a ogni cambio ospite e i rendiconti di fine mese? Excel, WhatsApp, qualche app? Sto studiando uno strumento per semplificare questa parte e cerco 10 co-host disposti a raccontarmi in 20 minuti come lavorano. In cambio, un mese gratis quando sarà pronto. Scrivetemi in privato.

### Email alle imprese di pulizia
> Oggetto: Domanda veloce sui cambi Airbnb
>
> Buongiorno, sto sviluppando uno strumento che invia agli addetti alle pulizie i turni dei cambi ospite in automatico, con checklist e foto. Lavorate con host o co-host di affitti brevi? Mi piacerebbe capire in 15 minuti come ricevete oggi gli incarichi e cosa vi crea più problemi. Grazie, [nome e telefono]

## 3. Scheda intervista (20 minuti)

Regola d'oro: chiedi di fatti passati, non di opinioni sul futuro. Non presentare l'idea prima della domanda 7.

| # | Domanda | Cosa ascoltare |
|---|---|---|
| 1 | Quanti alloggi gestisci, di quanti proprietari, su quali portali? | Profilo: rientra nel target 2-10? |
| 2 | Raccontami l'ultimo cambio ospite: chi ha pulito, come l'hai avvisato, come hai controllato? | Passaggi manuali, strumenti usati |
| 3 | Ti è capitato un cambio andato storto negli ultimi 3 mesi? Cosa è successo e quanto ti è costato? | Gravità concreta (recensione negativa, rimborso, tempo) |
| 4 | Come prepari il rendiconto per i proprietari? Me lo mostri? Quanto tempo ci metti al mese? | Ore al mese, uso di Excel |
| 5 | Ti è mai capitato di dimenticare un adempimento (Questura, ISTAT, tassa)? Come li gestisci oggi? | Uso di Chekin o simili |
| 6 | Che strumenti paghi oggi e quanto al mese? Ne hai provati e lasciati? Perché? | Budget reale, motivi di abbandono |
| 7 | (Ora descrivi l'idea in due frasi.) Cosa ti servirebbe perché valga la pena usarlo? | Funzioni indispensabili, obiezioni |
| 8 | Lo proveresti un mese gratis? Dopo, a 6 € per alloggio al mese, continueresti? | Sì/no netto, prezzo accettabile |
| 9 | Conosci altri co-host che dovrei sentire? | Passaparola |

## 4. Registro risultati

| Nome | Alloggi | Strumenti oggi | Problema pulizie (0-3) | Problema rendiconti (0-3) | Paga già (€/mese) | Accetta pilota | Prezzo ok | Note |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

Punteggio problema: 0 = nessuno, 1 = fastidio, 2 = perde tempo ogni settimana, 3 = ha perso soldi o clienti.

## 5. Decisione dopo 14 giorni

- **Vai avanti** se almeno 4 co-host su 6 danno 2-3 a pulizie o rendiconti **e** almeno 3 accettano il pilota. Prossimo passo: MVP con `/replica-architect` e `/replica-build`.
- **Correggi** se il problema c'è ma è un altro (es. solo rendiconti, o solo adempimenti): riduci l'MVP a quella parte.
- **Fermati** se quasi tutti dicono che Excel e WhatsApp bastano: passa alla proposta B (scadenzario adempimenti) o al settore ASD.

Mandami il registro compilato e preparo io l'analisi e il piano dell'MVP.
