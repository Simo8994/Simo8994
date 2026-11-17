# Macro Outlook: istruzione operativa da e-mail

## Installazione (una volta)
1. In Outlook premi **Alt+F11** per aprire l'editor VBA.
2. Menu **File > Importa file…** e scegli `IstruzioniOperative.bas`.
3. In cima al modulo imposta:
   - `MODELLO_Q93`: percorso del modello Q93.00 in "Modelli Poli"
   - `CARTELLA_WORD`: cartella dove salvare i Word (il percorso deve finire con `\`)
   - `CARTELLA_PDF`: lascialo vuoto per salvare il PDF nella stessa cartella del Word
   - `DESTINATARIO`: e-mail dell'ufficio tecnico
4. Salva e chiudi l'editor.
5. Aggiungi il pulsante: **File > Opzioni > Barra multifunzione** (oppure "Barra di accesso rapido"), categoria **Macro**, voce `CreaIstruzioneDaEmail`, poi **Aggiungi**.
6. Se le macro sono bloccate: **File > Opzioni > Centro protezione > Impostazioni macro**.
   Se l'azienda non lo permette, serve l'ok dell'IT.

## Uso
1. Seleziona (o apri) l'e-mail con le foto e le informazioni, poi premi il pulsante.
2. Scegli **No** per un'istruzione nuova, partendo dal modello Q93.00.
   Scegli **Sì** per un aggiornamento, partendo dal Word della revisione precedente:
   la revisione aumenta di 1 e il testo dell'e-mail viene aggiunto evidenziato in giallo.
3. Conferma i dati proposti: codice articolo, CAD, rev., fase, descrizione, macchina.
4. Il Word viene salvato col nome standard
   `CAD_rev.xx_fase yy descrizione_macchina_YYYYMMDD` e i campi vengono aggiornati.
5. Controlla e completa il documento in Word, poi premi **OK**:
   viene creato il PDF e si apre l'e-mail pronta da inviare.
