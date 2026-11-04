# Architecture: Officina (nome provvisorio), ricostruzione delle funzioni principali del modulo Scrum di WEPLADOO

Scope deciso: nucleo Commesse + bacheca Scrum settimanale + registrazione ore + carico utenti +
impostazioni base. Prodotto multi-azienda (ogni cliente è una `org`), usabile anche per un'azienda
sola. Kanban, Calendario, Cadence, Dashboard e import arrivano dopo il nucleo.

## Stack

| layer | choice | why |
| --- | --- | --- |
| web | Next.js 15 (App Router) + TypeScript | server actions per le mutazioni, un solo progetto per UI e API |
| styling | Tailwind + token di replica-design | componenti veloci da fare, temi per org |
| UI board | dnd-kit | drag and drop accessibile da tastiera e touch (la bacheca si usa anche da telefono) |
| database | Postgres su Supabase | RLS per org, storage e auth nello stesso servizio |
| ORM | Drizzle | SQL esplicito, migrazioni da `schema.sql` |
| auth | Supabase Auth (email + password, reset via email) | il login dell'originale è username/password; username vive in `memberships` |
| realtime | Supabase Realtime su `activities` | la bacheca si aggiorna quando un collega sposta una card |
| payments | Stripe Checkout + Billing, per postazione | solo se venduto come SaaS; non serve per uso interno |
| email | Resend | reset password, inviti, riepilogo settimanale |
| jobs | Vercel Cron | chiusura timer dimenticati, riepilogo settimanale, avvisi milestone |
| files | Supabase Storage | copertine dei tipi di progetto, file di import |
| hosting | Vercel (regione EU) | dati di aziende italiane: tenerli in UE |

Una base dati, nessun microservizio.

## Schema

Tables: 22 + 1 vista (`weekly_load`). Access rules: Row Level Security su `org_id`
(`is_member` per i dati operativi, `is_admin` per le impostazioni). Vedi `replica/schema.sql`.

Verificato su Postgres 16 locale: lo schema si carica; rifiutati settimana non di lunedì,
"eseguito" senza data, secondo timer acceso per la stessa persona, scrittura nelle impostazioni
da un membro semplice, scrittura in un'altra org; `weekly_load` restituisce 150 min pianificati /
75 registrati sul dato di prova.

Scelte:
- Settimana = `date` del lunedì ISO (`week_start`), con check. La card mostra "45/2026".
- Tempi in minuti interi. I tre tempi sulla card dell'originale li rendiamo come
  **stimato / registrato / residuo** (residuo = stimato − registrato, minimo 0). Se poi si scopre
  che l'originale intende altro, cambia solo la vista.
- `time_entries.minutes` è colonna generata; `ended_at is null` = timer acceso, al massimo uno per
  persona (indice unico parziale).
- Codici leggibili (`MAN26000037-001-01`) composti dal server: prefisso del tipo di progetto + anno
  a 2 cifre + progressivo per org e tipo, poi `-fase-attività`. Unici per org.
- `position` double per ordinare le card senza rinumerare la colonna.
- Su Supabase: `users` diventa `auth.users`, `current_user_id()` diventa `auth.uid()`.

Controlli nel data layer (non esprimibili con FK semplici): assegnatario, ufficio, fase e
predecessore devono appartenere alla stessa org dell'attività; il predecessore non deve creare cicli.

## API

Server actions e route handler; ogni chiamata passa da `requireMember(org)` o `requireAdmin(org)`
oltre alla RLS.

| method path | does | who | input | output | flow |
| --- | --- | --- | --- | --- | --- |
| POST /auth/login | accesso con username o email + password | pubblico | username, password | sessione | F01 |
| POST /auth/reset | invia link di reset | pubblico | email | 204 | F01 |
| GET /o/:org/scrum?week&office&user&pred | colonne della settimana con card e contatori | membro | filtri | {columns, cards} | F01 F04 |
| POST action moveActivity | cambia stato e/o posizione, imposta done_at | membro (proprie) / planner (tutte) | id, status, position, version | card | F01 |
| POST action createActivity | nuova attività, anche indiretta | membro | phase?, title, week, assignee, estimate | card | F01 |
| PATCH action updateActivity | modifica campi, assegna, sposta settimana | planner, o assegnatario sui propri campi | id, patch, version | card | F04 |
| POST action startTimer | apre time_entry (chiude quello acceso) | membro | activity_id | entry | F02 |
| POST action stopTimer | chiude il timer acceso | membro | - | entry | F02 |
| POST action logTime | ore a mano | membro | activity_id, start, end, note | entry | F02 |
| POST action reportDelay | causale di ritardo, alza l'allerta | membro | activity_id, reason_id, note | delay | F03 |
| GET /o/:org/scrum/load?week&office | carico per persona contro calendario | planner | settimana, ufficio | righe weekly_load + capacità | F04 |
| GET /o/:org/scrum/progress?week | eseguito vs pianificato della settimana | membro | settimana | totali per ufficio | F04 |
| GET /o/:org/commesse?status | elenco a card con filtri | membro | stati | commesse | F06 |
| POST action createCommessa | crea commessa, fasi e attività dal template del tipo | planner | tipo, cliente?, nome, quantità, portfolio | commessa | F05 |
| PATCH action updateCommessa | modifica / cambia stato | planner | id, patch | commessa | F05 |
| CRUD /o/:org/settings/* | utenti, divisioni, uffici, competenze, tipi progetto, attività, milestone, causali, calendari | admin | - | - | - |
| POST action inviteUser | invito via email | admin | email, ruolo, ufficio | membership | - |

Webhooks in: Stripe (`checkout.session.completed`, `customer.subscription.updated|deleted`), solo
versione SaaS. Webhooks out: nessuno nel nucleo.

Jobs:
- `close-stale-timers`, ogni ora: chiude i timer accesi da più di 12 h alla fine del turno del
  calendario e segnala l'utente.
- `milestone-alerts`, ogni giorno 06:00 Europe/Rome: alza `alert` sulle attività non eseguite con
  milestone nella settimana corrente o passata.
- `weekly-digest`, lunedì 07:00 Europe/Rome: email ai planner con carico e ritardi della settimana.

## The parts that bite

- time zones: settimana e giorni lavorativi si calcolano nel fuso dell'org (`orgs.timezone`), non del
  browser né in UTC; cambio ora legale nell'ultima settimana di ottobre e marzo.
- idempotency: webhook Stripe deduplicati per `event.id`; start/stop timer idempotenti (stop senza
  timer acceso = no-op).
- races: due persone spostano la stessa card. Si usa `updated_at` come versione: l'update passa solo se
  la versione coincide, altrimenti la UI ricarica la card. Il timer doppio è già bloccato dal DB.
- realtime: canale per org + settimana; il client applica le modifiche altrui senza perdere un drag in corso.
- multi-tenancy: RLS su ogni tabella + controllo "stessa org" sulle FK incrociate nel data layer.
- search: ricerca per codice e titolo con indice trigram quando le attività superano qualche migliaio.
- offline: non nel nucleo. Il reparto può avere rete scarsa: il timer salva l'inizio sul server subito,
  mai solo in locale.
- GDPR: le ore registrate sono dati personali dei dipendenti; eliminare un utente = disattivare la
  membership e anonimizzare il nome, le ore restano per i consuntivi di commessa. Hosting in UE.
- file: copertine max 2 MB, import CSV max 10 MB.

## Build order

1. Vertical slice (brutta ma funzionante)
   - screens: S01 login, S03 bacheca (una settimana, colonne, card, sposta), S10 modale attività minima
   - tables: orgs, users, memberships, offices, divisions, activities
   - routes: /auth/login, GET scrum, moveActivity, createActivity
   - fatto quando: due utenti della stessa org vedono la stessa bacheca e uno sposta una card
2. Must-haves
   - scrum: filtri ufficio/utente/predecessore, contatori, allerta e ritardo (delay_reasons, activity_delays), assegnatario
   - ore: time_entries, logTime, tre tempi sulla card
   - commesse: S02 elenco + chip di stato, createCommessa con fasi, milestone e "Scadenza milestone"
   - pianificazione: S11 carico utenti (weekly_load + work_calendars)
   - impostazioni: S13 utenti + inviti, S14 divisioni, S16 uffici, selettore sede in topbar
   - auth: reset password
3. Should-haves: timer avvia/ferma, attività indirette, S12 progresso settimanale, S17 tipi di progetto con
   template, S18/S19 milestone e catalogo attività, S21 causali, S22 calendari, S08 dashboard, job dei promemoria.
4. Could-haves: competenze, Kanban, Calendario, Cadence, import CSV con log, note di versione.
5. Fixes from replica-entrepreneur: da aggiungere quando avrà girato.
