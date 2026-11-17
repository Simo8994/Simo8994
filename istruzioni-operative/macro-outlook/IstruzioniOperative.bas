Attribute VB_Name = "IstruzioniOperative"
Option Explicit

' =====================================================================
'  Crea un'istruzione operativa Q93.00 da un'e-mail selezionata in Outlook
'  1) foto allegate + testo dell'e-mail -> modello Q93.00 (o revisione precedente)
'  2) salva il Word col nome standard e aggiorna i campi
'  3) dopo il tuo controllo: PDF + e-mail pronta per l'ufficio tecnico
' =====================================================================

' ====== DA IMPOSTARE (una volta sola) ======
Private Const MODELLO_Q93 As String = "C:\PERCORSO\Modelli Poli\Q93.00 istruzione operativa per attrezzaggi.docx"
Private Const CARTELLA_WORD As String = "C:\PERCORSO\attrezzaggi per paola\"
Private Const CARTELLA_PDF As String = ""      ' vuoto = stessa cartella del Word
Private Const DESTINATARIO As String = ""      ' indirizzo e-mail dell'ufficio tecnico (es. Mohammed)
Private Const MIN_KB_FOTO As Long = 30         ' immagini piu' piccole (loghi nelle firme) vengono ignorate
Private Const LARGH_MAX_CM As Single = 17      ' dimensione massima foto nel documento
Private Const ALT_MAX_CM As Single = 12
' ===========================================

Private Const TITOLO As String = "Istruzione operativa"

Public Sub CreaIstruzioneDaEmail()
    Dim mail As Object, wd As Object, doc As Object, tb As Object, c As Object, rg As Object
    Dim base As String, aggiornamento As Boolean, risp As VbMsgBoxResult
    Dim testo As String, art As String, cad As String, rev As String, fase As String
    Dim desc As String, mac As String, nome As String, percorsoDoc As String, percorsoPdf As String
    Dim foto As Collection, f As Variant, passi As String, rigaFoto As Long

    On Error GoTo Errore

    ' --- e-mail selezionata o aperta ---
    If TypeName(Application.ActiveWindow) = "Inspector" Then
        Set mail = Application.ActiveInspector.CurrentItem
    ElseIf Application.ActiveExplorer.Selection.Count > 0 Then
        Set mail = Application.ActiveExplorer.Selection.Item(1)
    End If
    If mail Is Nothing Then MsgBox "Seleziona prima l'e-mail.", vbExclamation, TITOLO: Exit Sub
    If mail.Class <> 43 Then MsgBox "L'elemento selezionato non e' un'e-mail.", vbExclamation, TITOLO: Exit Sub

    ' --- nuova o aggiornamento ---
    risp = MsgBox("E' l'aggiornamento di un'istruzione gia' esistente?" & vbCrLf & vbCrLf & _
                  "Si' = scegli il Word della revisione precedente" & vbCrLf & _
                  "No = parti dal modello Q93.00 vuoto", vbYesNoCancel + vbQuestion, TITOLO)
    If risp = vbCancel Then Exit Sub
    aggiornamento = (risp = vbYes)

    Set wd = ApriWord()
    If aggiornamento Then
        base = ScegliFile(wd)
        If base = "" Then Exit Sub
        LeggiNomeFile NomeSenzaEstensione(base), cad, rev, fase, desc, mac
        If rev <> "" Then rev = Format(Val(rev) + 1, "00")
    Else
        base = MODELLO_Q93
        If Dir(base) = "" Then MsgBox "Modello non trovato:" & vbCrLf & base & vbCrLf & _
            "Imposta MODELLO_Q93 in cima alla macro.", vbCritical, TITOLO: Exit Sub
    End If

    ' --- proposte ricavate dall'e-mail (oggetto + testo) ---
    testo = mail.Subject & vbLf & mail.Body
    If cad = "" Then cad = Trova(testo, "\b\d{3}\.\d{4}\.\d{2}\b")
    If rev = "" Then rev = Trova(testo, "rev\.?\s*(\d+)", 1)
    If fase = "" Then fase = Trova(testo, "fase\s*(\d+)", 1)
    art = Trova(testo, "\b\d{10}\.\d{2}\b")

    ' --- crea il documento (copia del modello o della revisione precedente) ---
    Set doc = wd.Documents.Add(Template:=base)
    Set tb = doc.Tables(1)
    If art = "" Then art = TestoCella(tb.Cell(1, 2))

    ' --- dati (proposti, modificabili) ---
    art = InputBox("Codice articolo", TITOLO, art):            If art = "" Then GoTo Annulla
    cad = InputBox("Codice CAD", TITOLO, cad):                 If cad = "" Then GoTo Annulla
    rev = InputBox("Revisione", TITOLO, IIf(rev = "", "00", rev)): If rev = "" Then GoTo Annulla
    fase = InputBox("Numero fase", TITOLO, fase):              If fase = "" Then GoTo Annulla
    desc = InputBox("Descrizione breve della fase (es. tranciatura)", TITOLO, desc): If desc = "" Then GoTo Annulla
    mac = InputBox("Codice macchina (lascia vuoto se non serve)", TITOLO, mac)

    rev = Format(Val(rev), "00")
    nome = cad & "_rev." & rev & "_fase " & fase & " " & desc
    If Trim(mac) <> "" Then nome = nome & "_" & Trim(mac)
    nome = PulisciNome(nome & "_" & Format(Date, "yyyymmdd"))

    ' --- compila ---
    ScriviCella tb.Cell(1, 2), art
    rigaFoto = RigaDopo(tb, "Foto o disegni")
    If rigaFoto = 0 Then MsgBox "Nel modello non trovo la riga 'Foto o disegni'.", vbCritical, TITOLO: GoTo Annulla
    Set c = tb.Cell(rigaFoto, 1)

    passi = PassiDaCorpo(mail.Body)
    If passi <> "" Then
        If aggiornamento Then
            Set rg = FineCella(c)
            rg.InsertAfter vbCr & "DA E-MAIL (" & Format(Date, "dd/mm/yyyy") & "):" & vbCr & passi
            rg.HighlightColorIndex = 7          ' giallo: da sistemare e poi togliere
        Else
            c.Range.Text = passi
        End If
    End If

    Set foto = SalvaFoto(mail)
    For Each f In foto
        InserisciFoto wd, doc, c, CStr(f)
    Next

    ' --- salva Word col nome standard + aggiorna campi ---
    percorsoDoc = CARTELLA_WORD & nome & ".docx"
    If Dir(percorsoDoc) <> "" Then
        If MsgBox("Esiste gia':" & vbCrLf & percorsoDoc & vbCrLf & "Sovrascrivere?", vbYesNo + vbExclamation, TITOLO) = vbNo Then GoTo Fine
    End If
    doc.SaveAs2 FileName:=percorsoDoc, FileFormat:=16
    AggiornaCampi doc
    doc.Save

    doc.Activate
    wd.Activate
    If MsgBox("Documento salvato:" & vbCrLf & nome & vbCrLf & vbCrLf & _
              "Controlla e completa il documento in Word (passi, ALERT, parametri, foto)." & vbCrLf & _
              "Poi premi OK: salvo, creo il PDF e preparo l'e-mail." & vbCrLf & _
              "Annulla = mi fermo qui (il Word resta salvato).", vbOKCancel + vbInformation, TITOLO) = vbCancel Then GoTo Fine

    ' --- PDF + e-mail ---
    AggiornaCampi doc
    doc.Save
    AggiornaCampi doc            ' SAVEDATE aggiornato al salvataggio appena fatto
    doc.Save
    percorsoPdf = IIf(CARTELLA_PDF = "", CARTELLA_WORD, CARTELLA_PDF) & nome & ".pdf"
    doc.ExportAsFixedFormat OutputFileName:=percorsoPdf, ExportFormat:=17

    With Application.CreateItem(0)
        .To = DESTINATARIO
        .Subject = "Istruzione operativa " & nome
        .Body = "Ciao," & vbCrLf & "in allegato l'istruzione operativa " & nome & "." & vbCrLf
        .Attachments.Add percorsoPdf
        .Display                  ' controlli tu e premi Invia
    End With
Fine:
    Exit Sub
Annulla:
    If Not doc Is Nothing Then doc.Close SaveChanges:=False
    Exit Sub
Errore:
    MsgBox "Errore: " & Err.Description, vbCritical, TITOLO
End Sub

' ---------------------------------------------------------------------
Private Function ApriWord() As Object
    Dim w As Object
    On Error Resume Next
    Set w = GetObject(, "Word.Application")
    On Error GoTo 0
    If w Is Nothing Then Set w = CreateObject("Word.Application")
    w.Visible = True
    Set ApriWord = w
End Function

Private Function ScegliFile(wd As Object) As String
    Dim fd As Object
    wd.Activate
    Set fd = wd.FileDialog(3)        ' msoFileDialogFilePicker
    fd.Title = "Scegli la revisione precedente"
    fd.InitialFileName = CARTELLA_WORD
    fd.AllowMultiSelect = False
    fd.Filters.Clear
    fd.Filters.Add "Word", "*.docx;*.doc"
    If fd.Show = -1 Then ScegliFile = fd.SelectedItems(1)
End Function

' Ricava CAD/rev/fase/descrizione/macchina da un nome tipo
' 017.0301.93_rev.03_fase 30 tranciatura_2051_20230503
Private Sub LeggiNomeFile(ByVal n As String, cad As String, rev As String, fase As String, desc As String, mac As String)
    Dim re As Object, m As Object
    If Left(n, 1) = "#" Then n = Mid(n, 2)
    Set re = CreateObject("VBScript.RegExp")
    re.IgnoreCase = True
    re.Pattern = "^(.+?)_rev\.?(\d+)_fase[ _]*(\d+)[ _]*(.*?)(?:_(?!\d{8}$)([^_]+))?(?:_(\d{8}))?$"
    If re.Test(n) Then
        Set m = re.Execute(n)(0)
        cad = m.SubMatches(0): rev = m.SubMatches(1): fase = m.SubMatches(2)
        desc = m.SubMatches(3): mac = m.SubMatches(4)
    End If
End Sub

Private Function Trova(ByVal testo As String, ByVal patt As String, Optional ByVal gruppo As Long = 0) As String
    Dim re As Object, m As Object
    Set re = CreateObject("VBScript.RegExp")
    re.Pattern = patt
    re.IgnoreCase = True
    If re.Test(testo) Then
        Set m = re.Execute(testo)(0)
        If gruppo = 0 Then Trova = m.Value Else Trova = m.SubMatches(gruppo - 1)
    End If
End Function

' Righe del corpo e-mail -> passi numerati "1) ..." (si ferma al messaggio citato)
Private Function PassiDaCorpo(ByVal corpo As String) As String
    Dim righe() As String, i As Long, t As String, n As Long, out As String
    righe = Split(Replace(corpo, vbCrLf, vbLf), vbLf)
    For i = 0 To UBound(righe)
        t = Trim(Replace(Replace(righe(i), vbTab, " "), Chr(160), " "))
        If t Like "Da:*" Or t Like "From:*" Or t Like "-----*" Or t Like "Inviato:*" Or t Like "Sent:*" Or t Like "____*" Then Exit For
        If t <> "" And Not t Like "[[]cid:*" Then
            n = n + 1
            If Not t Like "#[).]*" And Not t Like "##[).]*" Then t = n & ") " & t
            out = out & t & vbCr
        End If
    Next
    If Len(out) > 0 Then out = Left(out, Len(out) - 1)
    PassiDaCorpo = out
End Function

Private Function SalvaFoto(mail As Object) As Collection
    Dim cart As String, a As Object, ext As String, p As String, i As Long, col As New Collection
    cart = Environ("TEMP") & "\IO_foto_" & Format(Now, "yyyymmddhhnnss") & "\"
    MkDir cart
    For Each a In mail.Attachments
        ext = LCase(Mid(a.FileName, InStrRev(a.FileName, ".") + 1))
        If InStr("|jpg|jpeg|png|bmp|gif|tif|tiff|", "|" & ext & "|") > 0 And a.Size >= MIN_KB_FOTO * 1024& Then
            i = i + 1
            p = cart & i & "_" & a.FileName
            a.SaveAsFile p
            col.Add p
        End If
    Next
    Set SalvaFoto = col
End Function

Private Sub InserisciFoto(wd As Object, doc As Object, c As Object, ByVal file As String)
    Dim rg As Object, sh As Object, wMax As Single, hMax As Single
    Set rg = FineCella(c)
    rg.InsertAfter vbCr
    rg.Collapse 0
    Set sh = doc.InlineShapes.AddPicture(FileName:=file, LinkToFile:=False, SaveWithDocument:=True, Range:=rg)
    sh.LockAspectRatio = -1
    wMax = wd.CentimetersToPoints(LARGH_MAX_CM)
    hMax = wd.CentimetersToPoints(ALT_MAX_CM)
    If sh.Width > wMax Then sh.Width = wMax
    If sh.Height > hMax Then sh.Height = hMax
    sh.Range.ParagraphFormat.Alignment = 1   ' centrata
End Sub

Private Function FineCella(c As Object) As Object
    Dim rg As Object
    Set rg = c.Range
    rg.MoveEnd 1, -1
    rg.Collapse 0
    Set FineCella = rg
End Function

Private Function TestoCella(c As Object) As String
    Dim t As String
    t = c.Range.Text
    TestoCella = Trim(Left(t, Len(t) - 2))
End Function

Private Sub ScriviCella(c As Object, ByVal t As String)
    Dim rg As Object
    Set rg = c.Range
    rg.MoveEnd 1, -1
    rg.Text = t
End Sub

Private Function RigaDopo(tb As Object, ByVal etichetta As String) As Long
    Dim i As Long
    For i = 1 To tb.Rows.Count - 1
        If InStr(1, TestoCella(tb.Cell(i, 1)), etichetta, vbTextCompare) > 0 Then RigaDopo = i + 1: Exit Function
    Next
End Function

Private Sub AggiornaCampi(doc As Object)
    Dim sr As Object, r As Object
    For Each sr In doc.StoryRanges
        Set r = sr
        Do While Not r Is Nothing
            r.Fields.Update
            Set r = r.NextStoryRange
        Loop
    Next
End Sub

Private Function NomeSenzaEstensione(ByVal p As String) As String
    p = Mid(p, InStrRev(p, "\") + 1)
    If InStrRev(p, ".") > 0 Then p = Left(p, InStrRev(p, ".") - 1)
    NomeSenzaEstensione = p
End Function

Private Function PulisciNome(ByVal s As String) As String
    Dim ch As Variant
    For Each ch In Array("\", "/", ":", "*", "?", """", "<", ">", "|")
        s = Replace(s, ch, "-")
    Next
    PulisciNome = Trim(s)
End Function
