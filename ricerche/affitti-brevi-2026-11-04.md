# Analisi di mercato: affitti brevi per piccoli host (Italia)

Data della ricerca: 2026-11-04 · Mercato: Italia · Cliente: host privati e piccoli co-host (1-10 alloggi)
Ipotesi usate: web app responsive, sviluppatore singolo con Claude, budget basso, MVP in 4-8 settimane.

## Sintesi
- **Correzione rispetto alla scansione generale:** la parte degli adempimenti è più coperta del previsto. Chekin costa **da 3,95 € per alloggio al mese** e include Alloggiati Web, ISTAT e tassa di soggiorno ([prezzi Chekin](https://chekin.com/it/pricing/)). Sulle recensioni degli ospiti ha voto 4,7 su 53.556 ([Trustpilot](https://www.trustpilot.com/review/chekin.com)). Competere lì sul prezzo non ha senso.
- **Dove ci sono spazi:** 1) gli host non sanno **quali obblighi valgono per loro** (regione, comune, scadenze); 2) i fornitori attuali hanno **assistenza scarsa, disdette difficili e guasti** che fanno perdere soldi; 3) il **coordinamento di pulizie e rendiconti** per i piccoli co-host non ha strumenti italiani noti. Il terzo punto è il meno provato.
- **Mia raccomandazione:** validare con interviste l'idea **"gestionale operativo per piccoli co-host"** (punto 3), da usare insieme a Chekin e non al suo posto. In alternativa, uno **scadenzario adempimenti per comune**, più facile da fare ma con bassa disponibilità a pagare.
- **Prossimo passo:** 10 interviste a co-host e host con 2-10 alloggi, prima di scrivere codice.

## Concorrenti

| Prodotto | Target | Prezzo (fonte, data) | Voto / n. recensioni | Forza | Debolezza | Italia |
|---|---|---|---|---|---|---|
| Chekin | Host e hotel | da 3,95 €/alloggio/mese; minimi da 3 o 20 unità poco chiari ([pricing](https://chekin.com/it/pricing/), nov 2026) | 4,7 su 53.556 recensioni, quasi tutte di ospiti ([Trustpilot](https://www.trustpilot.com/review/chekin.com)) | Adempimenti inclusi, prezzo basso, ospiti soddisfatti | Fotografare i documenti è stressante per gli ospiti (riepilogo Trustpilot) | Sì, molto presente |
| Vikey | Host, B&B | 4,90 €/mese per check-in online e burocrazia, 19,90 €/mese per self check-in ([Smoobu](https://www.smoobu.com/en/integrations/vikey)); da 14,90 €+IVA secondo [Avantio](https://support.avantio.com/en/articles/424800-vikey-business-information) | 4,1 su 584 recensioni ([Trustpilot](https://jp.trustpilot.com/review/vikey.it)) | Serrature e domotica | Guasti alle serrature, assistenza, check-in troppo invasivo per gli ospiti | Sì (startup italiana) |
| Smoobu | Piccoli host | prezzo non verificato in questa ricerca | 4,1 su 548 recensioni ([Trustpilot](https://www.trustpilot.com/review/smoobu.com?page=2)) | Channel manager economico | Disservizi, supporto lento, sincronizzazione con VRBO solo via iCal, addebiti dopo la disdetta | Sì |
| Lodgify | Host e gestori | n/d | 4,5 su 1.311 recensioni ([Capterra](https://www.capterra.it/compare/149847/160106/kross-booking-suite/vs/smoobu)) | Sito web e prenotazioni dirette | n/d | Sì |
| Kross Booking | Gestori, piccoli hotel | n/d | 4,4 su 13 recensioni (Capterra) | Assistenza in chat in italiano lodata ([Capterra](https://www.capterra.com/p/149847/Kross-Booking-Suite/reviews/)) | Campione troppo piccolo | Sì (italiano) |
| Turno, Breezeway, Properly | Pulizie e operazioni | n/d | 4,6-4,7 ([GetApp](https://www.getapp.ca/compare/111661/130003/properly/vs/breezeway)) | Turni di pulizia con checklist e foto | **Non ho trovato presenza o recensioni in italiano** | Non verificata |

**Alternative usate oggi:** inserimento manuale sui portali (Alloggiati Web, Ross1000/Turismo5, portali comunali per la tassa di soggiorno), Excel e calendario Airbnb condiviso con gli addetti alle pulizie.

**Dimensione del mercato (verificato):** 734.769 strutture registrate e 667.670 CIN rilasciati al 26/10/2026 ([PMI.it su dati del Ministero del Turismo](https://www.pmi.it/?p=502385)). Quanti siano piccoli host non lo so; il dato include anche le strutture alberghiere.

## Cosa lamentano gli utenti

Campione: **35 citazioni** da 4 fonti (Trustpilot Smoobu, Trustpilot Vikey, forum della community Airbnb Italia, Capterra), periodo dicembre 2024 – novembre 2026. Le citazioni in inglese sono riportate nella lingua originale. Trustpilot limita gli estratti a circa 125 caratteri.

### Tema 1: inaffidabilità tecnica che fa perdere soldi
- "L'inaffidabilita' di sistemi che gestiscono aspetti critici mi causa seri problemi." (Vikey, host, 1★, 27/09/2026, che segnala overbooking, tariffe errate e serrature bloccate) [Trustpilot](https://it.trustpilot.com/review/vikey.it?stars=1&stars=2)
- "La serratura Vikey dell'appartamento ha problemi in continuazione: l'ospite arriva e non riesce ad entrare." (Vikey, host, 1★, 21/04/2026)
- "In un solo giorno mi ha fatto perdere soldi di prenotazione e non vogliono prendersi le proprie responsabilità." (Vikey, 1★, 07/06/2025)
- "Lo sistema è nuivo e non funziina bene.E sempre pieno di problemi anche se hanno un tecnico solo per risolvere tutto" (Vikey, host, 1★, 10/10/2026)
- "The worst company ever. Stay away or your company it will bankrupt from their platform." (Smoobu, 1★, 16/06/2026, piattaforma non disponibile per molte ore) [Trustpilot](https://www.trustpilot.com/review/smoobu.com?page=2)
- "Instead of giving clear status updates there was almost no communication." (Smoobu, 2★, 15/06/2026, disservizio di oltre 8 ore)
- "Changing channel managers is time consuming and disruptive, so I strongly recommend choosing a better provider" (Smoobu, 1★, 27/12/2025, doppio booking non segnalato)
- "Vrbo is just doing ical sync. That is too little for a channel manager." (Smoobu, 3★, 17/12/2025)
- "Very raw app, I'd expect to see that being a QA in their team testing dev-server, not a paid client on production." (Smoobu, 1★, 18/04/2026)
- "We have been forced to upgrade to the new website builder but the text editors don't format correctly in HTML" (Smoobu, 1★, 18/02/2026)

### Tema 2: assistenza clienti assente o lenta
- "Sono quasi 2 anni che pago il servizio più di €30 al mese e non hanno un servizio clienti" (Vikey, 2★, 04/02/2026)
- "Il team di assistenza è spesso poco propenso ad aiutare – tant'è che adesso hanno sostituito l'assistenza con un assistente AI" (Vikey, 2★, 13/06/2025)
- "Assistenza clienti INESISTENTE" (Vikey, titolo di una recensione 2★, 02/11/2026)
- "Premessa: sono una host. Ad oggi non posso che sconsigliare il prodotto: se c'è un problema" (Vikey, 1★, 14/07/2026)
- "Horrible customer service" (Smoobu, 1★, 21/04/2026)
- "But I will not due to really bad customer service." (Smoobu, 1★, 27/04/2026, il commerciale non si è presentato a due appuntamenti)
- "Bad serviss, in some cases to resolve quickly some problems they only answering with in 24h" (Smoobu, 2★, 23/04/2026)
- "We are extremely disappointed at this point with the service of Smoobu." (Smoobu, 1★, 18/06/2026)
- **Controprova:** su Kross Booking un utente scrive che "l'assistenza attraverso chat in Italiano è molto veloce e competente" ([Capterra](https://www.capterra.com/p/149847/Kross-Booking-Suite/reviews/)). L'assistenza umana in italiano è apprezzata, quindi è un vantaggio che si può usare per distinguersi.

### Tema 3: disdette e addebiti scorretti
- "I canceled my service from this company, and then they tried to bill me for another year of service, which I never used." (Smoobu, 1★, 14/05/2026)
- "lack of customer service. even when you advise them not to renew service" (Smoobu, 1★, 07/01/2026)
- "Ho pagato la disinstallazione al tecnico che mi lasciato con il citofono fuori uso" (Vikey, 1★, 07/10/2026)
- "I am so dissapointed with Smoobu." (Smoobu, 1★, 23/04/2026, per un aumento del canone)

### Tema 4: confusione su quali obblighi valgono e dove
- "non sapevo di dover registrare gli ospiti oltre che su Alloggiati web e il portale del comune" (host da tre mesi, Lazio, 25/07/2025) [Airbnb Community](https://communitycenter.airbnb.it/forum/2d51a5c2-16fb-4016-833b-8f987dae813c/post/bGVnYWN5X2Nj_2135466)
- "mi sapete dire se airb si occupa di compilare i dati degli ospiti sulla piattaforma Ross1000? grazie" (12/11/2024) [Airbnb Community](https://communitycenter.airbnb.it/forum/074005e0-0626-4b7e-92f9-8bd3b1daab97/post/bGVnYWN5X2Nj_2014903)
- "Caro, da quello che mi risulta, il portale Ross1000 che si occupa dei flussi ISTAT, va registrato da parte nostra" (risposta di un altro host, 18/11/2024, che non è sicuro nemmeno lui)
- Altre discussioni del forum, riassunte e non citate testualmente:
  - dubbi su quando Ross1000 sia diventato attivo nel Lazio;
  - difficoltà a collegare Ross1000 ad Alloggiati Web e a capire il campo "ID appartamento";
  - procedure diverse tra Emilia-Romagna e Lazio.
  - Fonte: [risultati della community Airbnb](https://community.withairbnb.com/t5/Organizza-gli-affari/ROSS1000-ex-Turismo5/m-p/1591603/highlight/true).
- Tassa di soggiorno: tariffe non aggiornate su Airbnb (caso di Napoli) e incertezza sull'obbligo del Modello 21 a seconda del comune ([Chekin blog](https://chekin.com/it/blog/modello-21-tutto-cio-che-ce-da-sapere/), [Fiscomania](https://fiscomania.com/imposta-di-soggiorno-locazioni-brevi/)).

### Tema 5: check-in percepito come complicato dagli ospiti
- "Una buona parte di turisti non capisce il sistema. In più adesso è uscita una nuova legge" (Vikey, host, 2★, 03/12/2024)
- "Le istruzioni che leggono gli ospiti dopo aver cliccato sul link sono errate con il risultato che mi chiamano stressati" (Vikey, host, 1★, 04/11/2024)
- "Ho contrattato la Vikey per gestire il mio B&B a Roma ma gli ospiti non si trovano bene con questo sistema" (Vikey, 1★, 19/09/2026)
- "I agree that the selfie with ID is invasive" (Vikey, ospite, 1★, 29/09/2026)
- "Muy dificil todo el proceso de registro" (Vikey, ospite, 1★, 12/08/2026)
- "Sono un host ed utilizzo Vikey da due mesi. ... la piattaforma è difficoltosa da usare, non è per nulla intuitiva" (Vikey, 2★, 13/08/2026)
- **Controprova:** Chekin ha recensioni degli ospiti molto positive (78% a 5 stelle). Questo problema riguarda più Vikey che il mercato in generale.

### Tema 6: pulizie e coordinamento di co-host e proprietari
- **Non ho trovato lamentele testuali di host italiani.** Le guide consigliano di sincronizzare il calendario con le pulizie e di avere un addetto di riserva ([SmartOrder](https://www.smartorder.ai/resources/it/blog/how-to-find-cleaners-for-airbnb-it/)).
- I co-host fanno rendiconti periodici ai proprietari con prenotazioni, spese e commissioni ([Maison Métropole](https://www.maisonmetropole.com/cosa-fa-un-property-manager/), [GuestSuite](https://guestsuite.app/blog/tassazione-cohost-affitti-brevi)). Non so con quali strumenti li facciano.
- **Fatto nuovo:** dal 20/11/2026 Airbnb vieta agli host di chiedere agli ospiti mansioni da personale di pulizia ([Sbircialanotizia](https://www.sbircialanotizia.it/articoli/2026/10/23/airbnb-pulizie-2qpmw/)). Le pulizie a ogni cambio ospite diventano quindi tutte a carico di host o addetti. Il testo ufficiale della regola va verificato.
- Gli strumenti specializzati (Turno, Breezeway, Properly) sono in inglese. Non ho trovato una presenza in Italia.

## Segnali di domanda
- **Obblighi crescenti (verificato):** CIN obbligatorio dal 01/01/2025 e Airbnb toglie gli annunci senza ([Airbnb](https://news.airbnb.com/it/airbnb-dal-2025-rimuovera-gli-annunci-sprovvisti-di-cin/)); Alloggiati Web con sanzioni penali; ISTAT su portali regionali diversi; dichiarazione annuale della tassa di soggiorno entro il 30/06 con sanzioni dal 100 al 200% ([Fiscomania](https://fiscomania.com/imposta-di-soggiorno-locazioni-brevi/)).
- **Il mercato paga (verificato):** Vikey ha raccolto 1,6 milioni di euro ([Fortune Italia](https://www.fortuneita.com/?p=90165)); un host dichiara di pagare "più di €30 al mese" per Vikey.
- **Host nuovi e inesperti (verificato su un caso):** l'host che è "host da soli tre mesi" ignorava un obbligo. Che ce ne siano molti in questa situazione è una mia deduzione.
- **Professionalizzazione (dedotto):** esistono offerte di co-hosting con commissioni del 10-28% ([Attivita24](https://www.attivita24.com/blog/property-management-per-locazioni-brevi-fee-e-margini), [Milanobiz](https://www.milanobiz.it/property-manager-per-affitti-brevi-a-milano/)). I co-host gestiscono più alloggi per conto terzi e hanno bisogno di strumenti operativi.

## Classifica delle opportunità

| Tema | Frequenza | Gravità | Disp. a pagare | Fattibilità | Scopertura | Totale /25 |
|---|---|---|---|---|---|---|
| 4. Confusione sugli obblighi (scadenzario per comune) | 4 | 4 | 2 | 5 | 3 | **18** |
| 2. Assistenza scarsa (vantaggio da sfruttare, non un prodotto) | 5 | 3 | 3 | 4 | 3 | **18** |
| 1. Inaffidabilità tecnica (channel manager, serrature) | 5 | 5 | 4 | 1 | 2 | 17 |
| 3. Disdette e addebiti (vantaggio: mensile senza vincoli) | 3 | 3 | 3 | 5 | 3 | 17 |
| 6. Pulizie e rendiconti per co-host | 1 | 3 | 4 | 4 | 4 | 16 |
| 5. Check-in complicato per gli ospiti | 4 | 3 | 3 | 4 | 2 | 16 |

**Come leggere la classifica:**
- Il tema 1 è il problema più grave, ma una persona sola non può costruire un channel manager affidabile né gestire serrature.
- I temi 2 e 3 non sono prodotti: sono **promesse da fare con qualunque prodotto**, cioè assistenza umana in italiano e abbonamento mensile disdicibile con un clic.
- Il tema 4 è facile da costruire, ma la gente paga poco per le informazioni. In più, mantenere le regole di quasi 8.000 comuni è un lavoro enorme: si parte da una sola regione.
- Il tema 6 ha la scopertura migliore e clienti che paganoperché lo fanno per lavoro, ma le prove sono le più deboli. Per questo va verificato per primo con le interviste.

## Proposta di app A (consigliata, da validare): gestionale operativo per piccoli co-host
- **Problema:** chi gestisce 2-10 alloggi per conto di proprietari deve coordinare pulizie a ogni cambio ospite (ora tutte a suo carico per Airbnb), controllare che gli adempimenti siano fatti e fare un rendiconto mensile a ogni proprietario. Ipotesi: oggi lo fa con Excel, WhatsApp e il calendario. **Il problema è dedotto: nessuna citazione diretta.**
- **Cliente target:** co-host e piccoli gestori di città turistiche, che paga con la propria partita IVA. Si trovano nella rete co-host di Airbnb ([esempio Pula](https://www.airbnb.com/host/pula-italy/co-hosts)), nei gruppi Facebook di host e tra le imprese di pulizia specializzate.
- **MVP:**
  1. Calendario unificato da iCal (Airbnb e Booking, sola lettura): niente sincronizzazione bidirezionale, così si evita la fragilità del tema 1.
  2. Turni di pulizia generati in automatico a ogni check-out, assegnati all'addetto via link o WhatsApp, con checklist e foto.
  3. Rendiconto mensile in PDF per ogni proprietario: incassi, pulizie, commissione del co-host.
  4. Checklist degli adempimenti per alloggio (Alloggiati, ISTAT, tassa di soggiorno), con spunte e promemoria. **L'app non invia nulla ai portali**: chi vuole automatizzare usa Chekin.
  5. Assistenza umana in italiano e abbonamento mensile disdicibile con un clic (temi 2 e 3).
- **Fuori dall'MVP:** channel manager, prezzi dinamici, serrature, messaggi agli ospiti, invio automatico ai portali.
- **Differenziazione:** strumento italiano, pensato per chi gestisce per conto terzi; affidabilità perché legge soltanto i calendari; assistenza umana; nessun vincolo contrattuale.
- **Prezzo indicativo:** 5-8 € per alloggio al mese, cioè sopra Chekin (3,95-7,95 €) perché è un altro tipo di strumento, e sotto i 30 € che un host dichiara di pagare a Vikey. **È un'ipotesi da verificare nelle interviste.**
- **Rischi:**
  - Il bisogno potrebbe già essere coperto da Excel, che è gratis.
  - Airbnb ha strumenti per co-host interni.
  - Lodgify e Smoobu potrebbero aggiungere la gestione delle pulizie.
  - I link iCal hanno ritardi di aggiornamento.
  - GDPR: si trattano dati degli ospiti, quindi serve una nomina a responsabile del trattamento.

## Proposta di app B (alternativa): scadenzario adempimenti per host
- **Problema:** tema 4, con citazioni dirette.
- **MVP:** l'host indica comune, regione e tipo di alloggio; l'app risponde con la lista personalizzata di obblighi, portali e scadenze, e manda promemoria. Include un registro della tassa di soggiorno incassata, pronto per la dichiarazione annuale.
- **Rischi:** bassa disponibilità a pagare, perché i blog di Chekin e Lodgify spiegano le stesse cose gratis; lavoro continuo per tenere aggiornate le regole comunali.
- **Uso migliore:** versione gratuita per attirare utenti verso la proposta A, oppure strumento da offrire ai commercialisti che seguono gli host.

## Validazione in 7-14 giorni
1. **10 interviste**: 6 co-host o gestori con 2-10 alloggi e 4 host privati.
2. **Domande:**
   1. Raccontami l'ultimo cambio ospite: chi ha pulito, come l'hai avvisato, come hai controllato che fosse fatto?
   2. Come prepari il rendiconto per i proprietari? Me lo mostri? Quanto tempo ci metti al mese?
   3. Che strumenti paghi oggi e quanto? Ne hai abbandonati? Perché?
   4. Ti è mai capitato di dimenticare un adempimento (Questura, ISTAT, tassa)? Cosa è successo?
   5. Se ti dessi uno strumento che fa i turni di pulizia e i rendiconti in automatico, lo proveresti per un mese a 6 € per alloggio?
3. **Soglia di successo:** almeno 4 co-host su 6 descrivono un processo fatto a mano che li fa soffrire, e almeno 3 accettano un pilota. Se non succede, si passa alla proposta B o al settore ASD.

## Limiti della ricerca
- **Fonti non accessibili:** gruppi Facebook di host (la fonte più ricca per questo settore), Capterra Italia (errore 403), recensioni sugli store delle app, Reddit (nessun risultato utile).
- **Dati non trovati:**
  - lamentele testuali sul tema 6 (pulizie e rendiconti);
  - prezzo di Smoobu;
  - numero di piccoli host rispetto alle strutture professionali;
  - quali minimi di unità valgano davvero su Chekin.
- **Deduzioni non verificate:** che i co-host usino Excel e WhatsApp; che pagherebbero 5-8 € per alloggio; che gli strumenti di pulizia esteri siano assenti in Italia.
- Le recensioni su Trustpilot di Chekin sono soprattutto di ospiti, non di host: non dicono quanto sono soddisfatti gli host.
- Le recensioni negative sono un campione distorto: indicano i problemi, non quanti utenti sono scontenti.
- Questa analisi non è una consulenza legale o finanziaria.
