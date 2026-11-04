# Build log

App: `officina/` (Next.js 15.5.27, React 19, Tailwind 3 con soli token, dnd-kit). Livello dati finto in
memoria (`src/lib/data/fake.ts`) con le stesse firme di quello reale: replica-backend lo sostituisce
senza toccare le schermate. Dati di prova inventati.

| ID | data | stato | cosa manca | più difficile del previsto |
| --- | --- | --- | --- | --- |
| shell | 2026-11-04 | done | selettore sede non filtra | griglie CSS che si allargano su mobile: serve `minmax(0,1fr)` a ogni livello |
| S01 login | 2026-11-04 | done | auth vera, reset via email | - |
| S04 menu | 2026-11-04 | done | - | - |
| S03 bacheca | 2026-11-04 | partial | dettaglio attività (S10), segnalazione ritardo, avvio/stop timer, inserimento ore, realtime tra utenti (oggi serve ricaricare) | spostamento da tastiera e annunci per lettori di schermo; rollback e conflitti di versione |
| S02 commesse | 2026-11-04 | partial | creazione e dettaglio commessa (S09) | - |
| S05-S08, S09, S11-S24 | 2026-11-04 | stub | pagine segnaposto con titolo | - |

Verifiche fatte (Playwright, build di produzione):
- login errato mostra errore; login giusto porta alla bacheca; logout torna al login
- spostamento con tastiera (Spazio, frecce, Spazio) e con menu "Sposta"; un altro utente vede la modifica ricaricando
- un membro non può spostare le attività di altri: messaggio di errore e card ripristinata
- creazione attività con validazione del titolo; titolo di 80 caratteri troncato su 2 righe
- filtro "Solo le mie", settimana vuota con stato vuoto, chip di stato e stato "nessuna commessa"
- 390px e 1440px senza scroll orizzontale; nessun errore in console
Screenshot in `replica/clone-screens/`.

Da fare dopo: componenti in una route `/design` (oggi c'è l'anteprima statica in `replica/design/preview.html`);
filtri della bacheca richiudibili su mobile (occupano mezzo schermo).
