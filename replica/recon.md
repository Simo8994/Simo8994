# Recon map: WEPLADOO, modulo Scrum (web app, desktop + mobile browser)

Scope (proposto, da confermare): gestione commesse e attività dell'ufficio tecnico con
bacheca Scrum settimanale, registrazione ore e carico utenti. Esclusi per ora: Cadence,
Dashboard, Importer, Scrum Factory.
For: da confermare (uso interno di un'azienda manifatturiera / prodotto per PMI manifatturiere).
Date: 2026-11-04

> Nota sui termini: l'account usato è un account aziendale (fornito dal datore di lavoro su
> una piattaforma di AzzurroDigitale). Contratto di licenza e regole aziendali possono vietare
> di usarlo per costruire un prodotto concorrente: va verificato. Questa mappa descrive solo
> funzioni e flussi visti a schermo. Non contiene codice, API, logo o dati dei clienti.

## Sources

| # | source | URL | notes |
| --- | --- | --- | --- |
| 1 | pagina di login (pubblica) | https://fratellipoli.wepladoo.it/login | Angular + Material + PrimeNG, autore "AzzurroDigitale" nei meta |
| 2 | screenshot dell'utente: Commesse | replica/screens/S02-commesse.png | account proprio, mobile Safari |
| 3 | screenshot dell'utente: Scrum + menu | replica/screens/S03-*.png | account proprio, menu laterale aperto |
| 4 | ricerca web su WEPLADOO / AzzurroDigitale | https://craft.co/azzurrodigitale | nessuna documentazione pubblica del prodotto trovata |

Mancano: help center, listino, changelog (esiste un elenco novità in-app "v3.8.0", non visto), video.

## Core loop

Il responsabile assegna le attività delle commesse agli uffici e alle persone per la settimana;
ogni persona le sposta da Da fare a In corso a Eseguito, registra le ore e segnala i ritardi.

## Screens

| ID | screen | route / how to reach | purpose | key components | states seen |
| --- | --- | --- | --- | --- | --- |
| S01 | Login | /login (redirect da ogni route senza sessione) | accesso | campo username, campo password con mostra/nascondi, "Forgot password?", bottone Login disabilitato finché vuoto | vuoto |
| S02 | Commesse (elenco) | menu > Commesse | vedere e creare commesse | breadcrumb, chip filtro Stato (rimovibili), griglia di card con immagine o colore, FAB + | pieno, filtrato |
| S03 | Scrum (bacheca settimanale) | menu > Scrum (/scrum) | pianificare e avanzare le attività della settimana | selettore settimana [02/11 - 08/11], bottoni "Mostra/Nascondi carico utenti" e "Progresso settimanale", filtri Predecessore / Ufficio / Utente, colonne con contatore, card attività, FAB play e + | pieno, colonna vuota (In corso 0) |
| S04 | Menu laterale | icona hamburger | navigazione | voci con icona, voce attiva evidenziata, gruppo Impostazioni espandibile | aperto, Impostazioni chiuso/aperto |
| S05 | Kanban | menu > Kanban | probabilmente una bacheca per stato, non per settimana | non visto | - |
| S06 | Calendario | menu > Calendario | attività nel tempo | non visto | - |
| S07 | Cadence | menu > Cadence | guess: attività ricorrenti / riunioni periodiche | non visto | - |
| S08 | Dashboard | menu > Dashboard | indicatori | non visto | - |
| S09 | Dettaglio commessa | click su card S02 (guess) | fasi, attività, milestone | non visto | - |
| S10 | Dettaglio / modifica attività | click su card S03 o FAB + (guess) | dati attività, ore, assegnatario | non visto | - |
| S11 | Carico utenti | bottone in S03 | ore assegnate per persona nella settimana | non visto | - |
| S12 | Progresso settimanale | bottone in S03 | avanzamento della settimana | non visto | - |
| S13 | Impostazioni: Utenti | Impostazioni > Utenti | anagrafica utenti | non visto | - |
| S14 | Impostazioni: Divisioni | Impostazioni > Divisioni | sedi / stabilimenti (selettore "sede" in topbar) | non visto | - |
| S15 | Impostazioni: Competenze | Impostazioni > Competenze | skill degli utenti | non visto | - |
| S16 | Impostazioni: Uffici | Impostazioni > Uffici | reparti (filtro Ufficio in S03) | non visto | - |
| S17 | Impostazioni: Tipi di progetto | Impostazioni > Tipi di progetto | template di commessa (es. Manutenzione, Campionatura, Stampi) | non visto | - |
| S18 | Impostazioni: Milestone | Impostazioni > Milestone | tipi di scadenza | non visto | - |
| S19 | Impostazioni: Attività | Impostazioni > Attività | catalogo attività standard | non visto | - |
| S20 | Impostazioni: Bin | Impostazioni > Bin | guess: contenitori / code di lavoro | non visto | - |
| S21 | Impostazioni: Causali di ritardo | Impostazioni > Causali di ritardo | motivi standard di ritardo | non visto | - |
| S22 | Impostazioni: Calendari | Impostazioni > Calendari | giorni e ore lavorative | non visto | - |
| S23 | Impostazioni: Importer Log | Impostazioni > Importer Log | log delle importazioni da gestionale / ERP | non visto | - |
| S24 | Impostazioni: Scrum Factory | Impostazioni > Scrum Factory | guess: configurazione della bacheca Scrum | non visto | - |

Topbar (su tutte): menu, logo aziendale, icona assistente (robot), matita (modalità modifica, guess),
novità versione "v3.8.0", aiuto, selettore sede "Divisione", filtro globale, menu utente con avatar a iniziali.

## Flows

```
F01 Lavorare la propria attività della settimana
    S01 login -> S03 Scrum (settimana corrente) -> card in Da fare -> In corso (drag o play) -> Eseguito
    happy path clicks: ~4 (login, apri menu, Scrum, sposta card)
    edge: nessuna attività in settimana, attività senza assegnatario, milestone scaduta (icona !), allerta (campanella)

F02 Registrare ore su un'attività
    S03 -> FAB play (avvia timer, guess) oppure S10 -> inserisci ore -> salva
    edge: ore oltre la stima, ore su attività indiretta ("Lavoro indiretto di ufficio" / "Registrazione ore")

F03 Segnalare un ritardo
    S10 -> scegli causale (da S21) -> salva -> icona ! sulla card
    edge: ritardo su predecessore (filtro Predecessore)

F04 Pianificare la settimana di un ufficio
    S03 -> filtro Ufficio -> Mostra carico utenti (S11) -> assegna / sposta attività -> Progresso settimanale (S12)
    edge: persona sovraccarica, attività senza competenza richiesta

F05 Creare una commessa
    S02 -> FAB + -> tipo di progetto (S17), cliente, quantità, portfolio -> salva -> genera fasi e attività (guess)
    edge: commessa interna senza cliente (es. manutenzione), stato In attesa

F06 Filtrare le commesse per stato
    S02 -> chip Stato (Inserita / In corso / In attesa) -> rimuovi chip
```

## Components

| component | variants | states | used on |
| --- | --- | --- | --- |
| Topbar | - | sede selezionata | tutte |
| Side nav | voce, gruppo espandibile | attiva, hover, chiusa/aperta | tutte |
| Breadcrumb | - | - | S02 |
| Filter chip | Stato: valore, rimovibile | attiva | S02 |
| Select con label flottante | Predecessore, Ufficio, Utente | vuota, valorizzata | S03 |
| Week picker | settimana ISO + range date | - | S03 |
| Button pieno | primario blu | default, hover | S03 |
| FAB | + (crea), play (avvia) | - | S02, S03 |
| Commessa card | con immagine di copertina, con cerchio colorato | - | S02 |
| Board column | titolo + contatore | vuota, piena, scroll | S03 |
| Activity card | codice, titolo, scadenza milestone (settimana), descrizione, 3 tempi, catena progetto/commessa/cliente/fase/ufficio, avatar | normale, in ritardo (!), allerta (campanella), indiretta (trattino) | S03 |
| Avatar a iniziali | piccolo (card), grande (topbar) | - | S03, topbar |
| Text field con icona | username, password con toggle | vuoto, focus, errore (non visto) | S01 |

## Inferred data model

```
Division      id, name                                   (es. sede "Breganze")
              evidence: selettore in topbar, Impostazioni > Divisioni   confidence: high
Office        id, division_id, name, code                (es. "CAM e progr. st...")
              evidence: filtro Ufficio S03, Impostazioni > Uffici       confidence: high
User          id, username, name, initials, office_id, division_id
              evidence: topbar, avatar card, filtro Utente              confidence: high
Skill         id, name; UserSkill(user_id, skill_id, level?)
              evidence: Impostazioni > Competenze                       confidence: medium
Customer      id, name
              evidence: campo Cliente su S02, catena card S03           confidence: high
ProjectType   id, name, color, cover_image, activity_template?
              evidence: card S02 (Manutenzione, Campionatura, Stampi), Impostazioni > Tipi di progetto
              confidence: medium
Commessa      id, code, name, subtitle, project_type_id, customer_id (nullable),
              status (inserita | in_corso | in_attesa | ...), portfolio, quantity
              evidence: S02                                             confidence: high
Phase         id, commessa_id, code (…-001), name       (guess dal codice MAN26000037-001-01)
              confidence: guess
Milestone     id, commessa_id/phase_id, type, due_week (ISO week/year)
              evidence: "Scadenza milestone: 45/2026"                   confidence: high
ActivityType  id, name, default_office_id
              evidence: Impostazioni > Attività                         confidence: medium
Activity      id, code, title, description, phase_id, activity_type_id, office_id,
              assignee_id, week (ISO), status (da_fare | in_corso | eseguito | +1 colonna a sinistra non leggibile),
              estimated_minutes, logged_minutes, remaining_minutes (3 tempi sulla card; significato da verificare),
              predecessor_id, is_indirect, alert
              evidence: card S03, filtro Predecessore                   confidence: high (campi), guess (significato dei tempi)
TimeEntry     id, activity_id, user_id, start_at, end_at | minutes
              evidence: FAB play, "Registrazione ore"                   confidence: medium
DelayReason   id, name; ActivityDelay(activity_id, reason_id, note, at)
              evidence: icona ! su card, Impostazioni > Causali di ritardo  confidence: medium
WorkCalendar  id, division_id, working_days, hours_per_day, holidays
              evidence: Impostazioni > Calendari                        confidence: medium
ImportLog     id, source, started_at, status, rows, errors
              evidence: Impostazioni > Importer Log                     confidence: medium
```

Relationships: Division 1-n Office 1-n User; Customer 1-n Commessa; ProjectType 1-n Commessa;
Commessa 1-n Phase 1-n Activity; Commessa 1-n Milestone; Activity n-1 User (assignee);
Activity 1-n TimeEntry; Activity 0-1 Activity (predecessor); Activity 0-n ActivityDelay.

## Feature matrix

See `features.csv`. Must: 17, should: 10, could: 7, skip: 3.

## Out of scope (cannot or should not be cloned)

- Logo, immagini, nome WEPLADOO, nome e marchio dell'azienda: identità non nostre (replica-brand).
- Dati reali: commesse, clienti, utenti visti negli screenshot. Il clone parte vuoto.
- Integrazione con il gestionale / ERP dell'azienda dietro "Importer": si rifà solo un import CSV generico.
- Assistente AI (icona robot) e Scrum Factory: comportamento non visto, da valutare dopo.

## Size

Screens 24 (5 visti, 19 dedotti dal menu), flows 6, entities 15.
Hard parts: drag and drop della bacheca con colonne per settimana e filtri; calcolo del carico
utenti contro i calendari lavorativi; generazione di fasi e attività dai tipi di progetto;
timer e registrazione ore affidabili.
Size: L (un trimestre) per tutto il menu; M (qualche settimana) per il nucleo Commesse + Scrum + ore + Impostazioni base.

Da raccogliere per completare la mappa: screenshot di Kanban, Calendario, Cadence, Dashboard,
dettaglio commessa, dettaglio attività, Carico utenti, Progresso settimanale, colonna più a
sinistra della bacheca, e di 2-3 pagine di Impostazioni. Significato dei tre tempi sulla card.
