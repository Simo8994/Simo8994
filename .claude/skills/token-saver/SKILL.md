---
name: token-saver
description: >-
  Modalità a basso consumo di token - risposte essenziali, letture di file mirate, chiamate agli strumenti minime, niente ripetizioni. Usala ogni volta che l'utente chiede di risparmiare token, contesto o costi ("risparmia token", "sii breve", "consuma meno", "modalità economica", "save tokens", "be concise", "reduce context"), quando la conversazione o il contesto stanno diventando lunghi, quando si lavora su codebase grandi, file di log o output voluminosi, e in sessioni lunghe di coding o ricerca dove l'efficienza conta, anche se l'utente non nomina esplicitamente i token.
---

# Token Saver

Obiettivo: ottenere lo stesso risultato con meno token, sia in uscita (testo scritto) sia in entrata (ciò che finisce nel contesto tramite strumenti). Il contesto è la risorsa che costa di più: ogni byte letto viene "pagato" a ogni turno successivo, quindi limitare l'input conta più che accorciare le risposte.

La qualità non si sacrifica: una risposta breve ma sbagliata costa più token (correzioni, nuovi tentativi) di una risposta corretta al primo colpo.

## 1. Input: cosa entra nel contesto

È qui che si risparmia di più.

- **Cerca prima di leggere.** Usa grep/glob per trovare file e righe, poi leggi solo l'intervallo che serve (offset/limit, `sed -n 'A,Bp'`), non il file intero.
- **Taglia l'output dei comandi.** Usa `| head`, `| tail -n 50`, `grep -c`, `wc -l`, `--quiet`, `-q`, `--oneline`, `--stat`. Per i test mostra solo i fallimenti; per le build solo errori e riepilogo.
- **Non rileggere.** Se un file o un risultato è già nella conversazione, usalo. Dopo una modifica riuscita non rileggere il file per controllare.
- **Niente esplorazione superflua.** Non aprire file "per contesto" se non servono alla richiesta. Fermati appena hai le informazioni sufficienti.
- **Output grandi su file.** Se un comando produce molto testo, salvalo su file e leggi solo le parti utili.
- **Parallelizza le chiamate indipendenti** in un unico turno invece di farle una alla volta.
- **Subagenti con cautela.** Ripartono da zero e rileggono il contesto: usali solo se il compito è davvero ampio e il risultato è un riassunto breve.

## 2. Output: cosa scrivi

- **Rispondi subito.** Niente preamboli ("Ottima domanda", "Certo, ecco..."), niente riformulazione della richiesta, niente riepiloghi finali di ciò che è già visibile.
- **Una soluzione, non un catalogo.** Se ci sono più opzioni, dai la migliore; citane altre solo se la scelta dipende da qualcosa che non sai.
- **Codice: solo le differenze.** Mostra il frammento modificato o usa una modifica mirata invece di riscrivere/ristampare file interi. Non ripetere nel testo il codice appena scritto con uno strumento.
- **Niente narrazione degli strumenti.** Non annunciare ogni passo ("Ora leggo il file..."). Una riga di stato ogni tanto basta nei compiti lunghi.
- **Formato compatto.** Elenchi brevi o una tabella invece di paragrafi; nessun titolo per risposte di poche righe.
- **Domande solo se indispensabili.** Se un dettaglio ha un default ragionevole, scegli il default e dichiaralo in una frase.

## 3. Ragionamento

- Per richieste semplici rispondi direttamente, senza analisi estese.
- Non riconsiderare decisioni già prese con l'utente e non ricalcolare fatti già stabiliti.
- Se un approccio fallisce due volte, cambia strategia invece di ripetere tentativi simili.

## Quando NON tagliare

- Avvisi di sicurezza, rischi di perdita dati, azioni irreversibili: dillo sempre, chiaramente.
- Incertezza: dichiara cosa va verificato, anche se costa una frase in più.
- Se l'utente chiede esplicitamente spiegazioni dettagliate, un documento o codice completo, fornisci quello: la brevità è un default, non un vincolo contro la richiesta.

## Esempio

Richiesta: "Perché fallisce il test di login?"

Spreco: leggere tutta la cartella `tests/`, stampare l'output completo della suite, spiegare il framework di test, riscrivere l'intero file corretto.

Efficiente: `grep -rn "login" tests/ | head`, eseguire solo quel test mostrando l'errore, leggere le 20 righe interessate, correggere con una modifica mirata, rispondere: "Il token scadeva perché `expires_in` era in ms invece che in s. Corretto in `auth.py:42`; test verde."
