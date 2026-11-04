# Componenti di Officina

Base: shadcn/ui (Radix) + Tailwind con `tailwind.tokens.cjs`. Icone: Lucide (ISC).
Nessun logo, immagine o testo dell'originale: etichette e stati vuoti sono scritti da zero.
Focus visibile ovunque: anello 2px `focus`, offset 2px. Animazioni disattivate con
`prefers-reduced-motion`.

Etichette nostre (diverse dall'originale): colonne **Backlog · Da iniziare · In lavorazione · Completate**;
"Carico persone", "Andamento settimana", "Nuova attività", "Nuova commessa".

```
AppHeader
  layout    alto 56px (layout.header), bg surface, bordo inferiore border; niente banda colorata
  contenuto bottone menu, logo dell'org (o nome), spazio, selettore sede, aiuto, novità, menu utente
  states    sede selezionata, menu utente aperto
  a11y      <header>, landmark; bottone menu con aria-expanded e aria-controls
  used on   tutte

SideNav
  variants  fissa (>= lg, 264px), drawer (< lg, sopra un overlay)
  item      icona 20px + etichetta sm/500, alto 44px, radius md
  states    default, hover (surface-sunken), attiva (bg accent-soft, text on-accent-soft, barra 3px accent a sinistra), focus
  gruppo    "Impostazioni" espandibile, chevron ruotato
  a11y      <nav aria-label="Principale">, voce attiva aria-current="page"; drawer intrappola il focus, Esc chiude
  used on   tutte

Breadcrumb
  tokens    text-muted sm, separatore chevron, ultima voce text
  a11y      <nav aria-label="Percorso">, <ol>, ultima voce aria-current="page"
  used on   S02, S09

Button
  variants  primary (accent / on-accent), secondary (surface, bordo border, text), ghost, danger (danger / on-danger)
  sizes     sm 32px, md 40px, lg 48px (lg per i tocchi da reparto)
  states    default, hover (accent-hover), active, focus-visible, disabled (opacità 50%, cursor not-allowed), loading (spinner, etichetta resta per i lettori di schermo)
  tokens    radius md, font sm/600, padding x 16px
  a11y      vero <button>; loading con aria-busy
  used on   tutte

Fab
  variants  crea (+), avvia timer (play) / ferma timer (stop, colore danger)
  size      56px, radius pill, shadow pop, in basso a destra con 24px di margine
  a11y      aria-label obbligatorio ("Nuova attività", "Avvia timer su …"); su mobile non copre l'ultima card (padding inferiore della lista)
  used on   S02, S03

FilterChip
  struttura etichetta "Stato: In corso" + bottone x
  states    default (bg surface, bordo border), hover, focus; nessuno = testo "Tutti gli stati"
  a11y      la x è un <button aria-label="Rimuovi filtro Stato: In corso">
  used on   S02

Select (con etichetta sopra il campo)
  sizes     md 40px
  states    vuoto (placeholder text-muted), valorizzato, aperto, focus, disabled, errore (bordo danger + messaggio)
  a11y      Radix Select o combobox con ricerca quando le opzioni sono > 10 (utenti)
  used on   S03 (Ufficio, Persona, Dipendenze), S10

TextField
  variants  testo, password (toggle mostra/nascondi), numero, minuti (h:mm)
  states    vuoto, focus, compilato, errore (messaggio sotto, aria-describedby), disabled
  tokens    bordo border-input (3.79:1), radius md, alto 40px
  used on   S01, S10, impostazioni

WeekPicker
  struttura freccia indietro · "Sett. 45 · 2–8 nov 2026" · freccia avanti · "Oggi"
  regole    settimana ISO nel fuso dell'org
  a11y      frecce con aria-label "Settimana precedente/successiva"; tasti PagSu/PagGiù sulla bacheca
  used on   S03, S11, S12

CommessaCard
  struttura riquadro superiore 120px (colore del tipo di progetto o copertina caricata dall'org), codice xs/600 text-muted, nome lg, righe chiave/valore sm (Cliente, Stato, Portfolio, Quantità)
  states    default, hover (shadow pop), focus, stato come Badge
  empty     valore mancante = "—" in text-muted
  tokens    bg surface, radius lg, shadow card, bordo border
  a11y      tutta la card è un link (<a>) con nome accessibile = nome commessa
  used on   S02

Badge
  variants  neutral (surface-sunken / text), info (accent-soft / on-accent-soft), success, warning, danger (versioni -soft con testo pieno)
  tokens    xs/500, radius pill, padding 2px 8px
  used on   S02, S03, S10

BoardColumn
  struttura intestazione sticky "Da iniziare" + contatore Badge, lista card scrollabile
  states    vuota (testo "Nessuna attività" + bottone "Aggiungi"), piena, drop target (bordo tratteggiato accent), caricamento (3 skeleton)
  tokens    bg surface-sunken, radius lg, min-width layout.board-column-min, gap 8px
  mobile    < md: una colonna alla volta con tab sopra (Backlog / Da iniziare / …), swipe tra colonne
  a11y      role="list" con aria-label colonna e numero; annunci live su spostamento
  used on   S03

ActivityCard
  struttura riga 1: codice (mono xs) + titolo sm/600 (max 2 righe)
            riga 2: "Scadenza sett. 45" xs text-muted, descrizione 1 riga
            riga 3: tre tempi con etichetta: Stimato · Registrato · Residuo (h:mm), residuo danger se < 0
            riga 4: percorso commessa (tipo › commessa › cliente › ufficio) xs text-muted, troncato, + Avatar assegnatario
  stati     normale; in ritardo (bordo sinistro 3px danger + icona AlertCircle + causale nel tooltip);
            allerta scadenza (icona Bell warning); indiretta (etichetta Badge neutral "Indiretta", nessun percorso);
            timer acceso (bordo sinistro success + tempo che scorre); trascinata (shadow drag, rotazione 1°); focus
  tokens    bg surface, radius md, shadow card, padding 12px
  a11y      card focusabile; Invio apre il dettaglio; Spazio la prende, frecce la spostano tra colonne/posizioni, Spazio la lascia, Esc annulla (dnd-kit keyboard sensor); le icone di stato hanno testo nascosto
  used on   S03

Avatar
  variants  iniziali (default), foto caricata dall'utente
  sizes     24px (card), 32px (header)
  tokens    colore di fondo calcolato dal nome tra 6 tinte con testo AA
  a11y      alt / aria-label = nome completo
  used on   S03, header, S11

LoadBar (Carico persone)
  struttura nome + barra orizzontale pianificato / capacità + valore "32h / 40h"
  states    sotto 80% (accent), 80–100% (warning), sopra 100% (danger, con testo "+4h oltre")
  a11y      role="meter" con aria-valuenow / aria-valuemax; il colore non è l'unico segnale (testo)
  used on   S11

Dialog / Sheet
  variants  dialog centrato (desktop), sheet dal basso (mobile) per il dettaglio attività
  states    aperto, salvataggio (bottone loading), errore (banner danger in alto), conflitto ("Qualcuno ha modificato questa attività. Ricarica")
  a11y      Radix Dialog: focus trap, Esc, titolo collegato
  used on   S10, conferme

Toast
  variants  info, successo, errore; azione "Annulla" dopo uno spostamento di card
  durata    5s, pausa al passaggio del mouse
  a11y      regione aria-live polite (errore: assertive)
  used on   tutte

EmptyState
  struttura icona Lucide 40px text-muted, titolo base/600, frase sm text-muted, bottone primary
  testi     "Nessuna commessa con questi filtri" · "Settimana libera: nessuna attività pianificata" · "Nessun ritardo segnalato"
  used on   S02, S03, S11

Skeleton
  tokens    surface-sunken con pulsazione (ferma con reduced-motion)
  used on   caricamenti di S02, S03

LoginForm
  struttura card centrata 400px su bg, nome/logo dell'org, campi username/email e password, link "Password dimenticata?", bottone primary pieno
  states    vuoto (bottone disabilitato), invio (loading), errore credenziali (messaggio generico, senza dire quale campo), bloccato dopo 5 tentativi
  sfondo    tinta bg: niente foto o illustrazioni dell'originale
  used on   S01
```

Anteprima statica dei primitivi: `replica/design/preview.html` (screenshot in
`replica/design/preview.png`). Le versioni React vere nascono in `/replica-build` sopra shadcn/ui,
con una route `/design` che le mostra tutte.
