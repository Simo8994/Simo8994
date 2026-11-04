---
name: market-gap-finder
description: Analisi di mercato approfondita per scoprire quale app creare e quale problema risolverà. Mappa i concorrenti di un settore, raccoglie le lamentele reali degli utenti (App Store, Google Play, G2, Capterra, Trustpilot, Reddit, forum, gruppi di settore), misura i segnali di domanda, classifica le opportunità con un punteggio e chiude con una proposta di app concreta (target, MVP, prezzo, rischi, test di validazione). Usala ogni volta che l'utente chiede "che app potrei creare", "cosa manca nel mercato", "analisi di mercato", "di quale app c'è bisogno", "quali app la gente odia o usa malvolentieri", "trova un'idea di business/SaaS", "valida questa idea", "studia il settore X", "chi sono i concorrenti di X", oppure "what app should I build", "market research", "find a gap", "validate my idea", anche se non nomina esplicitamente l'analisi di mercato. Viene prima di /replica-recon e degli altri replica-*.
---

# Market Gap Finder

Obiettivo: arrivare a **una o più idee di app sostenute da prove**, non da intuizioni. Ogni affermazione importante deve poggiare su una fonte linkata oppure essere marcata come deduzione. Il valore della skill è proprio questo: l'utente userà il report per decidere dove investire settimane di lavoro e soldi, quindi un dato inventato o gonfiato fa più danni di un dato mancante.

Rispondi e scrivi il report nella lingua dell'utente (di default italiano).

## Tre modalità di ingresso

Capisci da dove parte l'utente e scegli il percorso:

- **A. Settore dato** ("barbieri", "affitti brevi", "artigiani"): mappa il settore → concorrenti → lamentele → opportunità → proposta.
- **B. App data** ("cosa odiano gli utenti di Fresha?"): parti dalle recensioni di quell'app e dei 3-5 concorrenti diretti → opportunità → proposta.
- **C. Nessun punto di partenza** ("cosa potrei creare?"): proponi 5-8 settori candidati scelti con i criteri della sezione "Shortlist iniziale", fai uno scan rapido (passi 2-4 in versione leggera, 2-3 fonti a settore), poi approfondisci i 1-2 migliori. Chiedi prima all'utente se ha un settore che conosce o contatti: è il fattore che più aumenta le probabilità di vendere.

## Inquadramento (prima di cercare)

Servono quattro dati. Ricavali dalla conversazione; chiedi solo quelli che mancano davvero, in una sola domanda. Se l'utente non risponde, usa i default e dichiarali nel report.

| Dato | Default |
|---|---|
| Paese/mercato | Italia (più confronto con mercato EN per i concorrenti) |
| Tipo di cliente | Piccole imprese e professionisti (B2B) |
| Piattaforma | Web app responsive, mobile se il caso d'uso lo richiede |
| Vincoli dell'utente | Sviluppatore singolo con Claude, budget basso, MVP in 4-8 settimane |

## Processo

### 1. Mappa dei concorrenti

Trova 5-10 prodotti che oggi risolvono (anche male) il problema. Includi le alternative "povere" che le persone usano davvero: Excel, WhatsApp, carta, agenda, gestionali generici. Spesso il vero concorrente è un foglio di calcolo.

Per ogni concorrente annota: nome, link, target, prezzo pubblico (con fonte e data), punti di forza, presenza in Italia (lingua, adempimenti locali, pagamenti locali), voto medio e numero di recensioni sugli store/directory.

### 2. Raccolta lamentele

È il cuore della skill. Leggi `references/fonti.md` per le query di ricerca per ciascuna fonte.

- Cerca recensioni da 1-3 stelle e thread di sfogo, privilegiando gli ultimi 24 mesi.
- Raccogli **citazioni testuali** con link, fonte, data e (se visibile) tipo di utente. Non parafrasare dentro le virgolette, non tradurre senza dirlo, non inventare citazioni: se non trovi prove su un tema, scrivi che non ne hai trovate.
- Punta ad almeno 30 citazioni per l'analisi completa (modalità A/B). Se ne trovi meno, dichiara il numero e che il campione è debole.
- Annota anche le richieste di funzionalità ("vorrei che...", "manca...") e i workaround ("uso Excel accanto a...", "ho dovuto pagare anche X per...").

### 3. Segnali di domanda

Le lamentele dicono cosa non va; i segnali di domanda dicono se qualcuno pagherebbe per la soluzione. Cerca:

- ricerche tipo "alternativa a X", "X costa troppo", "programma per [attività]";
- domande ricorrenti su forum e gruppi di settore;
- concorrenti che crescono, raccolgono fondi o alzano i prezzi (il mercato paga);
- obblighi normativi nuovi o in arrivo (creano domanda forzata: fatturazione, registrazioni, privacy);
- offerte di lavoro o freelance pagati per fare a mano ciò che l'app automatizzerebbe.

Non inventare dimensioni di mercato. Se citi un numero (fatturato, numero di imprese, utenti), riporta la fonte; se è una stima tua, mostra il calcolo e marcala come stima.

### 4. Classificazione dei problemi

Raggruppa le citazioni in temi (es. "prezzo che sale con gli utenti", "assistenza assente", "manca X per l'Italia"). Per ogni tema assegna un voto 1-5 su:

- **Frequenza**: quante citazioni indipendenti, su quante fonti.
- **Gravità**: fastidio o perdita di soldi/clienti/tempo.
- **Disponibilità a pagare**: chi si lamenta è un cliente pagante? Cita prezzi o cambi di fornitore?
- **Fattibilità**: una persona sola può risolverlo in un MVP senza dati proprietari o integrazioni bloccate?
- **Scopertura**: nessun concorrente lo risolve bene, soprattutto nel mercato scelto.

Punteggio = somma (max 25). Mostra la tabella completa: così l'utente vede perché un'opportunità vince e può dissentire sui singoli voti.

### 5. Proposta di app

Per le 1-3 opportunità migliori, scrivi:

- **Problema** in una frase, con le 2-3 citazioni più forti.
- **Cliente target** preciso (chi paga, chi usa, dove trovarlo).
- **MVP**: 3-6 funzionalità indispensabili e cosa resta fuori di proposito.
- **Differenziazione**: perché il cliente lascerebbe il concorrente (deve collegarsi ai temi del passo 4).
- **Prezzo indicativo** ragionato sui prezzi pubblici dei concorrenti.
- **Rischi**: legali (marchi, brevetti, termini d'uso, GDPR), dipendenza da dati o API di terzi, concorrenza dei grandi, difficoltà di acquisizione clienti.
- **Validazione in 7-14 giorni** prima di scrivere codice: 5-10 interviste con domande pronte, landing page con lista d'attesa, prevendita o pilota gratuito. Indica una soglia chiara di successo (es. "almeno 3 su 10 accettano un pilota").

### 6. Passaggio successivo

Chiudi indicando il prossimo passo concreto. Se l'idea richiede di studiare un'app esistente come riferimento, suggerisci `/replica-recon`; per il nome e il rebrand `/replica-brand`; per prezzi e landing `/replica-launch`. Se l'utente vuole solo il report, fermati.

## Shortlist iniziale (modalità C)

Preferisci settori con queste caratteristiche, perché sono quelli dove una persona sola ha chance reali:

- il software si paga già (mercato dimostrato) ma i prodotti sono vecchi, cari o pensati per un altro paese;
- non servono effetti di rete o dati proprietari (evita social, marketplace, mappe);
- c'è un obbligo locale o una abitudine locale che i grandi ignorano;
- i clienti sono raggiungibili direttamente (associazioni, gruppi, porta a porta);
- modello ad abbonamento possibile.

## Report

Usa il modello in `references/template-report.md`. Salva il report come `ricerche/<settore-o-app>-<AAAA-MM-GG>.md` nella cartella di lavoro e, nella risposta in chat, dai solo la sintesi (3-5 righe con l'opportunità migliore e il prossimo passo) più il percorso del file. Se l'utente vuole condividerlo, offri di pubblicarlo come pagina.

## Regole di onestà

- Distingui sempre **verificato** (con link), **dedotto** (ragionamento tuo) e **non trovato**.
- Indica la data della ricerca: prezzi e recensioni cambiano.
- Non presentare l'analisi come consulenza legale o finanziaria.
- Se le fonti sono bloccate o scarse (es. gruppi Facebook privati, store non indicizzati), dillo e suggerisci come l'utente può raccogliere i dati da sé.
- Le recensioni negative sono un campione distorto: chi è soddisfatto scrive meno. Usale per trovare problemi, non per stimare quanti utenti sono scontenti.
