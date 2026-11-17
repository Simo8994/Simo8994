"""Professional editable PDF (AcroForm): plan, safety, complete shopping list, quantity sheet,
job cards with materials/tools/steps/errors, drying times, notes.  python3 lista_pdf.py out.pdf"""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white

pdfmetrics.registerFont(TTFont('DV', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
OUT = sys.argv[1]
W, H = A4
M = 42
ACC = HexColor('#7d6246'); INK = HexColor('#2b2622'); MUTED = HexColor('#7a716a'); LINE = HexColor('#d9d2c8')
HL = HexColor('#fff3b0'); HLB = HexColor('#e0c35a'); BAND = HexColor('#f3eee7'); WARN = HexColor('#a3402f'); TIP = HexColor('#3f6b4f')
TITLE = 'Umidità e muffa'
def asc(s):  # AcroForm fields use Helvetica: keep values ASCII-safe
    return s.replace('–', '-').replace('²', '2').replace('×', 'x').replace('’', "'").replace('°', ' gradi')

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle('Umidita e muffa - diagnosi, rimedi e polizza'); c.setAuthor('Piano lavori casa')
form = c.acroForm
st = dict(page=1, y=0, fid=0, section='')

def footer():
    c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(M, 34, W - M, 34)
    c.setFillColor(MUTED); c.setFont('DV', 7.5)
    c.drawString(M, 22, f'{TITLE} — {st["section"]}'); c.drawRightString(W - M, 22, f'Pagina {st["page"]}')

def top(title, sub=''):
    st['section'] = title
    c.setFillColor(ACC); c.rect(0, H - 64, W, 64, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('DVB', 17); c.drawString(M, H - 34, title)
    if sub: c.setFont('DV', 9); c.drawString(M, H - 51, sub)
    footer(); st['y'] = H - 88

def new_page(title=None, sub='continua'):
    c.showPage(); st['page'] += 1; top(title or st['section'], sub)

def need(h):
    if st['y'] - h < 48: new_page()

def wrap(text, font, size, width):
    out = []
    for para in text.split('\n'):
        words, cur = para.split(), ''
        for w_ in words:
            t = (cur + ' ' + w_).strip()
            if pdfmetrics.stringWidth(t, font, size) <= width: cur = t
            else: out.append(cur); cur = w_
        out.append(cur)
    return out

def band(text, color=ACC, size=11):
    need(34)
    y = st['y']
    c.setFillColor(BAND); c.rect(M, y - 19, W - 2 * M, 19, fill=1, stroke=0)
    c.setFillColor(color); c.rect(M, y - 19, 3, 19, fill=1, stroke=0)
    c.setFont('DVB', size); c.drawString(M + 9, y - 14, text)
    st['y'] -= 27

def sub(text):
    need(22); c.setFillColor(ACC); c.setFont('DVB', 9.5); c.drawString(M, st['y'] - 9, text.upper()); st['y'] -= 16

def para(text, font='DV', size=9, color=INK, indent=0, gap=4):
    lines = wrap(text, font, size, W - 2 * M - indent)
    need(len(lines) * 12 + gap)
    c.setFont(font, size); c.setFillColor(color)
    for ln in lines:
        c.drawString(M + indent, st['y'] - 9, ln); st['y'] -= 12
    st['y'] -= gap

def box_line(text, kind='check', color=INK, bold=False, prefix=''):
    """checkbox + wrapped text (kind: check / bullet / warn / tip)"""
    font = 'DVB' if bold or kind == 'warn' else 'DV'
    col = WARN if kind == 'warn' else TIP if kind == 'tip' else color
    tx = M + 22
    lines = wrap(prefix + text, font, 9, W - 2 * M - 22)
    need(len(lines) * 12 + 5)
    y = st['y']
    if kind == 'check':
        st['fid'] += 1
        form.checkbox(name=f'c{st["fid"]}', x=M + 3, y=y - 11, size=11, borderColor=ACC, fillColor=white, buttonStyle='check', borderWidth=1, forceBorder=True)
    else:
        sym = {'bullet': '•', 'warn': '!', 'tip': '✓'}[kind]
        c.setFillColor(col); c.setFont('DVB', 9.5); c.drawString(M + 6, y - 9, sym)
    c.setFont(font, 9); c.setFillColor(col)
    for ln in lines:
        c.drawString(tx, st['y'] - 9, ln); st['y'] -= 12
    st['y'] -= 5

def field(name, x, y, w, h=15, value='', multiline=False, size=8):
    form.textfield(name=name, value=asc(value), x=x, y=y, width=w, height=h, fontName='Helvetica', fontSize=size,
                   borderColor=LINE, fillColor=white, textColor=INK, borderWidth=0.6, forceBorder=True,
                   fieldFlags='multiline' if multiline else '')


def table(rows, widths, head=None, size=8.5):
    """simple wrapped table; rows = list of tuples of strings"""
    def draw(cells, bold, fill):
        lines = [wrap(t, 'DVB' if bold else 'DV', size, w - 10) for t, w in zip(cells, widths)]
        h = max(len(l) for l in lines) * 11 + 8
        need(h); y = st['y']
        if fill: c.setFillColor(fill); c.rect(M, y - h, sum(widths), h, fill=1, stroke=0)
        c.setStrokeColor(LINE); c.setLineWidth(0.5); c.line(M, y - h, M + sum(widths), y - h)
        x = M
        for ls, w in zip(lines, widths):
            c.setFont('DVB' if bold else 'DV', size); c.setFillColor(INK)
            for i, ln in enumerate(ls): c.drawString(x + 5, y - 11 - i * 11, ln)
            x += w
        st['y'] -= h
    if head: draw(head, True, BAND)
    for r in rows: draw(r, False, None)
    st['y'] -= 8

def steps(items):
    for i, t in enumerate(items, 1): box_line(t, 'check', prefix=f'{i}. ')

FULL = W - 2 * M
# =====================================================================================
top('Umidità e muffa', 'Diagnosi, rimedi passo passo, prevenzione e polizza del condominio — documento compilabile')
band('La situazione')
para('Casa al piano terra. Muffa sui muri a contatto con l\'esterno: in cucina (soprattutto dove c\'erano i mobili e vicino agli attacchi di acqua e gas) e nella stanza con il muro verde. La muffa sta nella fascia bassa, dal pavimento fino a circa 1 m, ed è più forte negli angoli.')
box_line('In cucina il parquet vicino al muro è annerito e le doghe si staccano: lì è arrivata acqua vera, non solo umidità dell\'aria. Prima di tutto va esclusa una perdita.', 'warn')
box_line('Non comprare materiali e non rifare muri o parquet finché non hai fatto le verifiche di pagina 2: la cura cambia completamente a seconda della causa.', 'warn')
band('Le tre cause possibili')
table([('Condensa', 'Muffa dietro i mobili, negli angoli e sui muri freddi; peggiora d\'inverno, quando si cucina o si fa la doccia; il muro in profondità è asciutto.', 'Antimuffa + fissativo + Aguaplast Anti-Condensa + pittura termica + ricambio d\'aria.'),
       ('Perdita d\'acqua', 'Macchie più forti intorno ad attacchi, scarichi o tubi; parquet rovinato in un punto; il contatore gira con i rubinetti chiusi.', 'Idraulico, poi asciugatura e ripristino. Può essere coperta dalla polizza del condominio.'),
       ('Risalita da terra', 'Fascia bassa e uniforme, aloni o polvere bianca (sali), zoccolo che si sfalda, muro umido anche d\'estate.', 'Tecnico: intonaco deumidificante ed eventuale barriera chimica. L\'Aguaplast qui NON va bene.')],
      [95, 220, FULL - 315], head=('Causa', 'Segnali', 'Rimedio'))

# =====================================================================================
new_page('Verifiche da fare', 'Fai le prove, scrivi il risultato e spunta la causa trovata')
def prova(titolo, testo, esito, fname):
    sub(titolo); steps(testo); para(esito, size=8.5, color=MUTED)
    need(24); c.setFont('DV', 8.5); c.setFillColor(INK); c.drawString(M, st['y'] - 11, 'Risultato:')
    field(fname, M + 55, st['y'] - 16, FULL - 55, 16); st['y'] -= 26
prova('1. Prova del foglio di alluminio',
      ['Asciuga la superficie e attacca un quadrato di alluminio da cucina 30×30 cm sulla zona macchiata, sigillando bene i 4 lati con nastro adesivo.',
       'Fallo in cucina e nella stanza con il muro verde, a 20–30 cm da terra.', 'Toglilo dopo 48 ore e guarda dove c\'è umidità.'],
      'Umidità sul lato verso la stanza = condensa. Umidità sul lato verso il muro = l\'acqua viene da dentro il muro (perdita o risalita).', 'r_alluminio')
prova('2. Prova del contatore dell\'acqua',
      ['Chiudi tutti i rubinetti e non usare acqua (lavatrice, lavastoviglie, WC compresi).', 'Fotografa il numero sul contatore.', 'Ricontrolla dopo 2–3 ore.'],
      'Se il numero è cambiato c\'è una perdita: chiama l\'idraulico e segui la pagina "Perdita".', 'r_contatore')
prova('3. Igrometro da muro (20–30 € al brico)',
      ['Misura lo stesso muro a 10 cm da terra e a 1,5 m d\'altezza.', 'Ripeti la misura dopo qualche giorno di stanza riscaldata e arieggiata.'],
      'Valore in basso molto più alto che in alto e che non scende = sospetto risalita o perdita. Valori bassi e uniformi = condensa.', 'r_igrometro')
prova('4. Osservazione',
      ['Per una settimana tieni la stanza a 18–20 °C e arieggia 10 minuti 3–4 volte al giorno.', 'Tocca il muro in basso: è ancora umido o freddo e bagnato?'],
      'Se si asciuga, era condensa. Se resta umido anche con l\'aria asciutta, è risalita o perdita.', 'r_osservazione')
sub('Causa trovata')
for t in ('Condensa', 'Perdita d\'acqua', 'Risalita da terra', 'Non chiaro: chiamo un tecnico'): box_line(t, 'check')

# =====================================================================================
new_page('Se è condensa', 'Procedura completa per i muri freddi verso l\'esterno')
sub('Materiali (per circa 5 m² di muro)')
table([('Antimuffa igienizzante per muri', '1 L', 'spray o liquido'), ('Fissativo Fassa FA 249', '1 secchio da 5 L (già comprato)', 'diluire 1 parte con 6–8 di acqua; ne servono meno di 0,5 L'),
       ('Aguaplast Anti-Condensa (Beissier)', '2 sacchi da 9 kg', 'circa 3 kg per m² a 5 mm di spessore'), ('Pittura termica anticondensa antimuffa', '2–2,5 L', 'resa circa 4–6 m²/L per mano: verifica in etichetta'),
       ('Guanti in nitrile, occhiali, mascherina FFP2, spugne, cazzuola americana, carta grana 120–180', '—', '')],
      [200, 120, FULL - 320], head=('Prodotto', 'Quantità', 'Note'))
sub('Giorno 1–2: antimuffa')
steps(['Proteggi il pavimento, metti guanti, occhiali e mascherina FFP2, apri la finestra. Termosifone vicino al muro spento o al minimo.',
       'Spruzza l\'antimuffa sulla macchia e per 30 cm intorno. Lascia agire 15–30 minuti senza correnti forti sul muro.',
       'Strofina con la spugna e risciacqua con acqua pulita. Raschia pittura che si stacca e intonaco che si sbriciola.',
       'Dopo 24 h, se ricompaiono puntini neri, ripeti.'])
sub('Giorno 2–4: asciugatura')
steps(['Termosifoni accesi normalmente (18–20 °C). Arieggia 10 minuti 3–4 volte al giorno. Se puoi, usa un deumidificatore.',
       'Niente stufette o phon puntati sul muro.', 'Prima di andare avanti il muro deve essere asciutto al tatto, non più freddo degli altri e senza puntini neri.'])
sub('Giorno 4: fissativo')
steps(['Diluisci il fissativo FA 249: 1 parte con 6–8 di acqua, mescola bene.', 'Spolvera il muro e stendi una mano a pennello o rullo su tutta la zona raschiata.', 'Aspetta 4–6 ore.'])
sub('Giorno 4–5: Aguaplast Anti-Condensa')
steps(['Impasta 0,6 L di acqua per ogni kg di polvere fino a una pasta liscia (lavorabile 5–6 ore).',
       'Prima mano di circa 3 mm con la cazzuola americana, su tutta la parete fredda, non solo sulla macchia.',
       'Dopo 12–24 h seconda mano di 2–3 mm: almeno 5 mm in totale. Sfuma i bordi verso le pareti vicine.',
       'Lascia asciugare 24–48 h, leviga con grana 120–180 e spolvera.'])
sub('Giorno 6–7: fissativo e pittura termica')
steps(['Una mano di fissativo diluito 1:6–8 e attesa di 4–6 h, solo se l\'etichetta della pittura lo permette (altrimenti usa il fondo che indica).',
       'Prima mano di pittura termica a rullo, piena. Dopo 4–6 h seconda mano.',
       'Arieggia nei giorni successivi; la pittura indurisce in 2–3 settimane.'])
box_line('Non usare su questi muri lo stucco in gesso (Litokol) né il rasante LC7: per riempire i buchi usa lo stesso Aguaplast.', 'warn')
box_line('Lavora tra +5 °C e +35 °C. Se la muffa torna entro un mese, non è condensa: rifai le verifiche.', 'warn')

# =====================================================================================
new_page('Se è una perdita o la risalita', 'Cosa fare e in che ordine')
band('Perdita d\'acqua')
steps(['Chiudi l\'acqua se la perdita è forte.', 'Fai foto e video di muri, parquet e attacchi dell\'acqua, con la data.',
       'Chiama l\'idraulico e fatti scrivere su fattura o rapporto la causa (es. "perdita dal raccordo dell\'attacco lavello"). Conserva il pezzo rotto.',
       'Avvisa subito l\'amministratore per scritto (email o PEC) perché apra il sinistro con l\'agenzia UnipolSai di Dueville.',
       'Aspetta il perito prima di rifare muro e parquet: fai solo gli interventi urgenti.',
       'Dopo la riparazione: asciugatura completa (anche settimane, meglio con deumidificatore), poi antimuffa e ripristino come per la condensa.'])
band('Risalita da terra')
steps(['Chiama un tecnico o un\'impresa specializzata in deumidificazione per una misura dell\'umidità nel muro.',
       'Rimedio tipico: togliere l\'intonaco rovinato fino a circa 50 cm sopra la macchia, intonaco deumidificante macroporoso, eventuale barriera chimica alla base del muro.',
       'Finitura solo con pitture traspiranti (silicati o calce), non lavabili plastiche.'])
box_line('In caso di risalita l\'Aguaplast Anti-Condensa non va bene: la sua etichetta lo esclude per umidità permanente o capillare.', 'warn')
box_line('Risalita e condensa possono esserci insieme: prima si risolve la risalita, poi si tratta la condensa.', 'tip')

# =====================================================================================
new_page('Polizza del condominio', 'UnipolSai Condominio&Servizi — Condominio Monte Bianco')
para('È la polizza del condominio e copre l\'intero fabbricato: le richieste di rimborso passano dall\'amministratore.')
table([('Perdita da tubi o attacchi dell\'acqua', 'Danni da acqua condotta: danni a muro, parquet e pittura', 'franchigia 250 €'),
       ('Ricerca del guasto', 'Spese per rompere, trovare e riparare il tubo, richiudere e sistemare (fino all\'1% della somma assicurata, max 50.000 €)', '—'),
       ('Tubo interrato che perde', 'Tubi interrati: spargimento d\'acqua fino a 2.500 €', 'franchigia 250 €'),
       ('Perdita nascosta (bolletta alta)', 'Perdite occulte: fino a 12.000 € all\'anno', '—'),
       ('Perdita da un vicino', 'RC spargimento d\'acqua del vicino', 'franchigia 250 €'),
       ('Pioggia entrata per un danno da temporale', 'Eventi atmosferici: acqua penetrata nel fabbricato', 'scoperto 10%, min. 300 €'),
       ('Mobili rovinati dall\'acqua', 'Contenuto delle singole unità: fino a 5.000 €', '—'),
       ('Condensa, risalita da terra, infiltrazione lenta dal muro', 'Normalmente escluse (fenomeni lenti, non accidentali)', 'non coperte')],
      [150, FULL - 250, 100], head=('Situazione', 'Garanzia e cosa rimborsa', 'A tuo carico'))
box_line('Il pezzo guasto (rubinetto, raccordo) di solito non è rimborsato: lo sono i danni che ha causato e le spese di ricerca e ripristino.', 'tip')
box_line('La polizza prevede la riparazione diretta: l\'assicurazione può mandare una sua impresa, senza che tu anticipi i soldi.', 'tip')
sub('Da chiedere all\'amministratore')
for t in ('La polizza è ancora attiva? (il documento è del 2018 con rinnovo automatico)', 'Copia del Fascicolo Informativo modello 7264, edizione 15/03/2018 (esclusioni e tempi di denuncia)',
          'Chi paga la franchigia: io o il condominio (regolamento di condominio)?', 'Apertura del sinistro e data del sopralluogo del perito'): box_line(t, 'check')

# =====================================================================================
new_page('Prevenzione e registro', 'Abitudini per non far tornare la muffa e diario delle misure')
for t in ('Cappa accesa mentre cucini e per 10 minuti dopo.', 'In bagno apri la finestra dopo la doccia o accendi l\'aspiratore.',
          'Arieggia 5–10 minuti 2–3 volte al giorno anche d\'inverno, con le finestre spalancate (non a ribalta per ore).',
          'Temperatura costante 18–20 °C; non spegnere del tutto il riscaldamento nelle stanze con muri esterni.',
          'Mobili, armadi e basi della cucina ad almeno 5–10 cm dai muri esterni.', 'Non stendere il bucato in casa nelle stanze con muffa; se serve, usa un deumidificatore.',
          'Umidità dell\'aria ideale: 40–60% (igrometro da ambiente, pochi euro).'): box_line(t, 'bullet')
st['y'] -= 6
band('Registro delle misure', size=10)
cols = [70, 110, 75, 75, FULL - 330]
y = st['y']; c.setFont('DVB', 8.5); c.setFillColor(INK)
x = M
for t, w in zip(('Data', 'Stanza / punto', 'Umid. aria %', 'Umid. muro %', 'Note'), cols): c.drawString(x + 3, y - 10, t); x += w
st['y'] -= 16
for r in range(14):
    need(20); x = M
    for k, w in enumerate(cols): field(f'reg_{r}_{k}', x + 1, st['y'] - 17, w - 3, 16); x += w
    st['y'] -= 20
c.save()
print('ok', OUT, 'pages', st['page'], 'fields', st['fid'])
