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
BAND = HexColor('#f3eee7'); WARN = HexColor('#a3402f'); TIP = HexColor('#3f6b4f')
TITLE = 'Piano lavori casa'
def asc(s):  # AcroForm fields use Helvetica: keep values ASCII-safe
    return s.replace('–', '-').replace('²', '2').replace('×', 'x').replace('’', "'").replace('°', ' gradi')

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle('Piano lavori casa - lista della spesa e istruzioni'); c.setAuthor('Piano lavori casa')
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

# =====================================================================================
# 1. COVER / PLAN
top('Piano lavori casa', 'Lista della spesa completa, calcolo quantità e istruzioni passo passo — documento compilabile')
para('Lavori previsti', 'DVB', 11, ACC)
for t in ['A. Muffa e umidità: risanare una mezza parete in cucina.',
          'B. Rasatura di un muro interno con intonaco, aggrappante e rasante.',
          'C. Riparazione di buchi grandi in una parete di cartongesso.',
          'D. Chiusura dei buchi di viti e tasselli sui muri interni.',
          'E. Chiusura dei buchi di viti sulle piastrelle del bagno.',
          'F. Pittura bianca di tutta la casa (soffitti e pareti).']:
    box_line(t, 'bullet')
st['y'] -= 4
para('Ordine dei lavori (da rispettare)', 'DVB', 11, ACC)
para('Protezione della casa → trattamento muffa → demolizione parti rovinate → riparazioni (cartongesso, buchi, intonaco) → aggrappante → rasatura → levigatura → fissativo → pittura. Ogni fase deve essere asciutta prima di passare alla successiva.')
para('Programma indicativo (una persona, lavori in parallelo dove possibile)', 'DVB', 11, ACC)
PLAN = [('Giorno 1', 'Proteggi mobili e pavimenti. 1ª passata antimuffa in cucina. Togli tasselli e viti. Rimuovi intonaco che si sbriciola. Ritaglia i buchi del cartongesso a forma regolare.'),
        ('Giorno 2', '2ª passata antimuffa se serve. Rinforzi e toppe nel cartongesso + 1ª passata stucco giunti con nastro. Intonaco su buchi profondi. Stucco sui buchi delle viti. Stucco epossidico sulle piastrelle.'),
        ('Giorno 3', '2ª passata stucco giunti (cartongesso). 2ª passata stucco sui buchi profondi. Aggrappante sul muro in cemento.'),
        ('Giorno 4', '1ª mano di rasante sul muro da rasare e sulla parete della cucina (se asciutta).'),
        ('Giorno 5–6', 'Levigatura creste. 2ª mano di rasante + frattazzino. Stucco di finitura sul cartongesso.'),
        ('Giorno 7–12', 'Asciugatura rasature (3–7 giorni). Intanto: fissativo e pittura dei soffitti e delle stanze senza riparazioni.'),
        ('Giorno 12–14', 'Levigatura finale e spolveratura. Fissativo sulle parti riparate. Pittura: 1ª mano, dopo 4–6 h 2ª mano.')]
for d, t in PLAN:
    lines = wrap(t, 'DV', 9, W - 2 * M - 92)
    need(len(lines) * 12 + 6)
    c.setFont('DVB', 9); c.setFillColor(ACC); c.drawString(M + 4, st['y'] - 9, d)
    c.setFont('DV', 9); c.setFillColor(INK)
    for ln in lines:
        c.drawString(M + 92, st['y'] - 9, ln); st['y'] -= 12
    st['y'] -= 4
st['y'] -= 2
box_line('Temperature di lavoro: tra +5 e +30 °C, niente sole diretto o stufe puntate sul muro. Con freddo e umidità i tempi di asciugatura si allungano anche del doppio.', 'tip')
box_line('Se la parete della cucina resta umida al tatto dopo i giorni di asciugatura, NON rasare e NON pitturare: va prima risolta la causa (perdita o risalita).', 'warn')

# =====================================================================================
# 2. SAFETY
new_page('Sicurezza e preparazione', 'Da fare prima di iniziare')
for t, k in [
    ('Mascherina FFP2/FFP3 durante levigatura, uso della mola e trattamento della muffa.', 'check'),
    ('Occhiali protettivi con mola, levigatrice, antimuffa e lavori sopra la testa (soffitti).', 'check'),
    ('Guanti in nitrile per antimuffa, stucco epossidico, rasanti e fissativi; guanti da lavoro per tagli e cartongesso.', 'check'),
    ('Arieggiare sempre le stanze; non mangiare e non lasciare animali nei locali durante i trattamenti.', 'check'),
    ('Non mescolare mai prodotti chimici diversi (antimuffa, detergenti, anticalcare, ammoniaca).', 'warn'),
    ('Prima di forare o fare tracce: verificare che non passino tubi o cavi (cercametalli o seguire la linea verticale/orizzontale di prese e interruttori).', 'warn'),
    ('Togliere la corrente al quadro prima di lavorare vicino a prese e scatole elettriche; coprire le prese con nastro di carta.', 'check'),
    ('Svuotare le stanze o raccogliere i mobili al centro e coprirli con teli; coprire pavimento e battiscopa.', 'check'),
    ('Nastro di carta su infissi, battiscopa, interruttori, piastrelle e bordi che non vanno toccati.', 'check'),
    ('Tenere a portata un secchio d\'acqua pulita per lavare subito gli attrezzi: rasante e stucchi induriti rovinano spatole e cazzuola.', 'tip'),
    ('Smaltimento: sacchi e polveri di cantiere vanno all\'isola ecologica; i barattoli vuoti di pittura asciutti nel secco o in ecocentro secondo il comune.', 'tip')]:
    box_line(t, k)

# =====================================================================================
# 3. SHOPPING LIST
new_page('Lista della spesa', 'Spunta quando hai comprato. Quantità precompilate dove possibile: correggile dopo il calcolo a pagina successiva.')
y = st['y']
c.setFont('DV', 7.5); c.setFillColor(MUTED)
c.drawString(M + 2, y, 'Preso'); c.drawString(M + 24, y, 'Articolo e specifica'); c.drawString(W - M - 218, y, 'Quantità'); c.drawString(W - M - 128, y, 'Uso'); c.drawString(W - M - 68, y, '€ / negozio')
st['y'] -= 10
LISTA = [
    ('Muffa', [
        ('Antimuffa igienizzante per muri (sali d\'ammonio quaternario o perossido), spray o liquido', '1 L', 'A'),
        ('Spugne per pulire la muffa', '3-4', 'A'),
        ('Stracci in cotone o microfibra', '1 conf.', 'A'),
    ]),
    ('Fondi e aggrappanti', [
        ('Aggrappante per cemento/calcestruzzo liscio (primer al quarzo)', '1 conf.', 'B'),
        ('Fissativo all\'acqua per interni (vale anche per cartongesso)', '1 L ogni 10-15 m2', 'A-F'),
    ]),
    ('Intonaci, rasanti e stucchi', [
        ('Intonaco bianco premiscelato per interni (calce o gesso), sacco', '1 sacco', 'B-D'),
        ('Rasante-collante cementizio per muri in cemento, sacco', '1,2-1,5 kg/m2 x mm', 'B'),
        ('Rasante fine di finitura per interni (gesso o calce)', '1 sacco', 'B'),
        ('Rasante deumidificante / traspirante a calce (parete cucina)', '1-2 sacchi', 'A'),
        ('Rete in fibra di vetro per rasatura (maglia 4x4 mm circa)', '1 rotolo', 'A-B'),
        ('Stucco in pasta pronto per interni (buchi piccoli)', '1 kg', 'D'),
        ('Stucco in polvere per interni (buchi grandi e profondi)', '1-5 kg', 'D'),
        ('Stucco per giunti cartongesso (1ª passata con nastro)', '5 kg', 'C'),
        ('Stucco di finitura per cartongesso (o unico giunti+finitura)', '1 conf.', 'C'),
        ('Stucco epossidico bicomponente bianco / kit ripara-ceramica con smalto', '1 kit', 'E'),
    ]),
    ('Cartongesso', [
        ('Lastra di cartongesso standard 12,5 mm (anche mezza lastra)', '1', 'C'),
        ('Profilo metallico a C o listelli di legno 2-3 cm per rinforzo dietro la toppa', '1 barra', 'C'),
        ('Viti autoperforanti per cartongesso 25 mm (fosfatate)', '1 conf.', 'C'),
        ('Nastro per giunti in carta microforata', '1 rotolo', 'C'),
        ('Seghetto per cartongesso (lama a punta)', '1', 'C'),
    ]),
    ('Pittura', [
        ('Pittura bianca traspirante per prima mano (o la lavabile diluita)', '1 L/10 m2', 'F'),
        ('Pittura bianca lavabile traspirante per interni (finitura)', '1 L/10 m2 x 2 mani', 'F'),
        ('Pittura antimuffa bianca per cucina e bagno', '2,5-5 L', 'A-F'),
        ('Rullo a pelo medio 22-25 cm + ricambio', '1 + 1', 'F'),
        ('Prolunga telescopica per rullo (soffitti)', '1', 'F'),
        ('Pennello piatto 5 cm (angoli e bordi) + pennellino 2-3 cm', '2', 'F'),
        ('Vaschetta per rullo con griglia', '1', 'F'),
        ('Nastro di carta per pittori 25-38 mm', '3-4 rotoli', 'F'),
        ('Teli o carta per coprire i pavimenti', 'per tutte le stanze', 'F'),
    ]),
    ('Attrezzi', [
        ('Cazzuola americana sottile inox 28-32 cm (rasare)', '1', 'B'),
        ('Spatole inox 6 / 10 / 20 cm', '3', 'B-D'),
        ('Frattazzino in spugna a grana fine', '1', 'B'),
        ('Spugna per rasare', '1', 'B'),
        ('Secchi da muratore', '2', 'tutti'),
        ('Frusta miscelatrice per trapano', '1', 'B'),
        ('Livella laser', '1', 'B-C'),
        ('Taglierino + lame di ricambio (verifica 9 o 18 mm)', '1 conf.', 'C-D'),
        ('Dischi per mola da muro', '1 conf.', 'A-B'),
        ('Avvitatore / trapano (se non ce l\'hai)', '-', 'C'),
        ('Metro, matita, squadra', '-', 'C'),
        ('Scala o trabattello', '-', 'F'),
    ]),
    ('Levigatura', [
        ('Dischi abrasivi per levigatrice grana 120 e 180', '1 conf. x tipo', 'B-C'),
        ('Sacco in tessuto per levigatrice', '1', 'B-C'),
        ('Carta vetrata a mano grana 120 e 180 + tampone', '1 + 1', 'C-D'),
    ]),
    ('Protezione e pulizia', [
        ('Mascherine FFP2/FFP3 con filtri', '1 conf.', 'tutti'),
        ('Occhiali protettivi', '1', 'tutti'),
        ('Guanti in nitrile', '1 conf.', 'A-E'),
        ('Guanti da lavoro', '1 paio', 'C'),
        ('Teli e sacchi copri-mobili', '1 conf.', 'F'),
        ('Alcool denaturato (sgrassare piastrelle)', '1', 'E'),
        ('Sacchi per macerie', '1 conf.', 'tutti'),
    ]),
]
for cat, items in LISTA:
    band(cat, size=10)
    for name, qty, use in items:
        lines = wrap(name, 'DV', 8.5, W - 2 * M - 250)
        need(max(18, len(lines) * 11 + 6))
        y = st['y']; st['fid'] += 1; k = st['fid']
        form.checkbox(name=f'p{k}', x=M + 4, y=y - 12, size=11, borderColor=ACC, fillColor=white, buttonStyle='check', borderWidth=1, forceBorder=True)
        c.setFont('DV', 8.5); c.setFillColor(INK)
        for i, ln in enumerate(lines): c.drawString(M + 24, y - 9 - i * 11, ln)
        field(f'q{k}', W - M - 218, y - 14, 86, value=qty)
        c.setFont('DV', 7.5); c.setFillColor(MUTED); c.drawString(W - M - 128, y - 9, use)
        field(f'n{k}', W - M - 68, y - 14, 68)
        st['y'] -= max(18, len(lines) * 11 + 6)
    st['y'] -= 4
band('Altro (righe libere)', size=10)
for _ in range(3):
    need(18); y = st['y']; st['fid'] += 1; k = st['fid']
    form.checkbox(name=f'p{k}', x=M + 4, y=y - 12, size=11, borderColor=ACC, fillColor=white, buttonStyle='check', borderWidth=1, forceBorder=True)
    field(f'v{k}', M + 24, y - 14, W - 2 * M - 250); field(f'q{k}', W - M - 218, y - 14, 86); field(f'n{k}', W - M - 68, y - 14, 68)
    st['y'] -= 18
st['y'] -= 4
para('Legenda "Uso": A muffa cucina · B rasatura · C cartongesso · D buchi viti muro · E piastrelle bagno · F pittura.', size=7.5, color=MUTED)
para('Tolti dalla lista perché non servono per questi lavori: candeggina, resina da esterno, colla da muro, cemento bianco, aggrappante per pittura (sostituito dal fissativo).', size=7.5, color=MUTED)

# =====================================================================================
# 4. QUANTITY SHEET
new_page('Calcolo quantità', 'Misura e scrivi i metri quadri: le formule sono accanto')
para('Come misurare: parete = larghezza × altezza; togli porte (circa 2 m²) e finestre. Soffitto = lunghezza × larghezza della stanza.', size=8.5, color=MUTED)
rows = [('Pareti totali da pitturare (m²)', 'Pittura finitura: m² × 2 mani ÷ 10 = litri'),
        ('Soffitti totali da pitturare (m²)', 'Pittura: m² × 2 mani ÷ 10 = litri (somma alle pareti)'),
        ('Superfici riparate o rasate (m²)', 'Fissativo: m² ÷ 12 = litri di prodotto da diluire'),
        ('Muro da rasare (m²)', 'Rasante: m² × 1,3 kg × spessore totale in mm (circa 3–4 mm)'),
        ('Parete cucina umida (m²)', 'Rasante traspirante: m² × 1,3 kg × 3 mm; pittura antimuffa: m² × 2 ÷ 10'),
        ('Bagno + cucina, pareti (m²)', 'Pittura antimuffa: m² × 2 mani ÷ 10 = litri')]
c.setFont('DV', 7.5); c.setFillColor(MUTED); c.drawString(M + 215, st['y'] - 4, 'm²'); c.drawString(M + 285, st['y'] - 4, 'risultato / quantità da comprare'); st['y'] -= 10
for lab, form_ in rows:
    need(40); y = st['y']; st['fid'] += 1; k = st['fid']
    c.setFont('DVB', 9); c.setFillColor(INK); c.drawString(M, y - 10, lab)
    field(f'mq{k}', M + 215, y - 15, 60, 17)
    field(f'ris{k}', M + 285, y - 15, W - 2 * M - 285, 17)
    c.setFont('DV', 7.5); c.setFillColor(MUTED); c.drawString(M, y - 27, form_)
    st['y'] -= 38
st['y'] -= 4
box_line('Compra circa il 10% in più di pittura e rasante: i lotti diversi di pittura possono avere tonalità leggermente diverse.', 'tip')
box_line('Esempio: 120 m² di pareti + 40 m² di soffitti = 160 m² × 2 mani ÷ 10 = 32 L, cioè 2 secchi da 14 L + 1 da 5 L.', 'tip')

# =====================================================================================
# 5. JOB CARDS
def card(title, goal, mats, tools, steps, errors, times):
    new_page(title, goal)
    sub('Materiali'); [box_line(m, 'bullet') for m in mats]
    sub('Attrezzi'); [box_line(t, 'bullet') for t in tools]
    sub('Procedura'); [box_line(s, 'check', prefix=f'{i}. ') for i, s in enumerate(steps, 1)]
    sub('Errori da evitare'); [box_line(e, 'warn') for e in errors]
    sub('Tempi'); para(times, size=8.5, color=MUTED)

card('A. Muffa e umidità — parete cucina', 'Eliminare la muffa e risanare la mezza parete prima della pittura',
     ['Antimuffa igienizzante per muri', 'Rasante deumidificante / traspirante a calce', 'Rete in fibra di vetro (se ci sono crepe)', 'Fissativo all\'acqua', 'Pittura antimuffa bianca', 'Spugne, stracci, guanti in nitrile, occhiali, mascherina FFP2'],
     ['Spatola 10 cm', 'Cazzuola americana', 'Frattazzino in spugna', 'Secchio + frusta'],
     ['Diagnosi: muffa solo d\'inverno, negli angoli, dietro i mobili, vicino a finestre = condensa. Muro bagnato dal basso, vicino al lavello o con macchie che si allargano = perdita o risalita: chiamare idraulico prima di continuare.',
      'Proteggi pavimento e mobili, arieggia la stanza, indossa guanti, occhiali e mascherina.',
      'Spruzza l\'antimuffa su tutta la zona macchiata più 30 cm intorno. Lascia agire 15–30 minuti (o come da etichetta).',
      'Strofina con la spugna e togli i residui con lo straccio inumidito. Ripeti dopo 24 h se le macchie non sono sparite.',
      'Batti il muro con le nocche: dove suona vuoto o si sbriciola, togli l\'intonaco con la spatola fino al supporto sano.',
      'Lascia asciugare il muro alcuni giorni, arieggiando ogni giorno. Il muro è pronto quando è asciutto al tatto e di colore uniforme.',
      'Ripristina gli spessori mancanti con il rasante traspirante (o intonaco a calce se il buco supera 1 cm).',
      'Rasatura in 2 mani con il rasante traspirante, come nella scheda B (passaggi 5–9).',
      'Dopo l\'asciugatura completa: fissativo, poi 2 mani di pittura antimuffa.'],
     ['Pitturare sopra la muffa senza trattarla: ritorna in poche settimane.', 'Usare rasanti o pitture non traspiranti (lavabili plastiche, smalti) su un muro umido.', 'Chiudere il muro se è ancora umido o se la causa non è risolta.', 'Mescolare l\'antimuffa con altri prodotti chimici.'],
     'Antimuffa: 15–30 min di posa, ripetizione dopo 24 h. Asciugatura muro: 2–7 giorni secondo l\'umidità. Rasante: 24–48 h tra le mani, 3–7 giorni prima di pitturare.')

card('B. Rasatura muro interno', 'Ottenere una parete liscia e pronta per la pittura',
     ['Aggrappante per cemento (solo su cemento o calcestruzzo liscio)', 'Intonaco bianco premiscelato (buchi e tracce oltre 1 cm)', 'Rasante-collante cementizio (muri in cemento) oppure rasante fine per interni', 'Rete in fibra di vetro (se ci sono crepe)', 'Fissativo all\'acqua'],
     ['Cazzuola americana sottile inox 28–32 cm', 'Spatole 10 e 20 cm', 'Frattazzino in spugna grana fine', 'Spugna per rasare', 'Secchi + frusta per trapano', 'Livella laser', 'Levigatrice con dischi 120 e 180 + sacco', 'Mascherina FFP2'],
     ['Togli polvere, chiodi, tasselli e parti che si staccano. Spazzola il muro.',
      'Controlla con la livella laser dove ci sono avvallamenti e segnali a matita.',
      'Se il muro è cemento liscio: stendi l\'aggrappante a rullo o pennello e lascialo asciugare 2–4 h (secondo scheda tecnica).',
      'Riempi tracce e buchi profondi oltre 1 cm con l\'intonaco; lascia asciugare 24 h (più strati se molto profondi).',
      'Inumidisci leggermente il muro se è molto assorbente (non sul cemento con aggrappante).',
      'Impasta il rasante con l\'acqua indicata sul sacco, con la frusta a bassa velocità, fino a crema senza grumi. Lascia riposare 3–5 min e rimescola. Prepara solo quello che usi in 1 h.',
      'Prima mano: 2–3 mm con la cazzuola a 30° circa, a zone di 1–2 m². Se ci sono crepe, annega la rete nel rasante fresco con sormonti di 10 cm.',
      'Aspetta 24–48 h. Togli le creste con la spatola o la carta 120 e spolvera.',
      'Seconda mano: 1–2 mm con la cazzuola quasi piatta. Quando è soda al tatto (circa 5–15 min per rasante fine, 15–40 min per cementizio) passa il frattazzino appena inumidito con movimenti circolari leggeri, sciacquandolo spesso.',
      'Lascia asciugare 3–7 giorni. Leviga leggermente con grana 180, spolvera e passa al fissativo (scheda F).'],
     ['Impastare troppo materiale: dopo 1–2 h fa presa e va buttato.', 'Aggiungere acqua a un impasto che ha già iniziato a indurire.', 'Passare il frattazzino troppo presto (porta via il materiale) o troppo tardi (non leviga più).', 'Scaldare il muro con stufe per asciugare prima: si formano crepe.', 'Pitturare su rasante ancora umido: macchie e distacchi.'],
     'Aggrappante 2–4 h. Intonaco 24 h per cm di spessore. Rasante: 24–48 h tra 1ª e 2ª mano, 3–7 giorni prima di fissativo e pittura.')

card('C. Buchi grandi nel cartongesso', 'Ricostruire la lastra con una toppa nuova e giunti invisibili',
     ['Lastra di cartongesso 12,5 mm', 'Profilo metallico a C o listelli di legno', 'Viti autoperforanti 25 mm', 'Nastro in carta microforata', 'Stucco per giunti + stucco di finitura', 'Fissativo'],
     ['Seghetto per cartongesso', 'Taglierino', 'Metro, squadra, matita', 'Avvitatore', 'Spatole 10 e 20 cm', 'Carta vetrata 180 + tampone', 'Mascherina'],
     ['Prima di tagliare, verifica che dietro non passino cavi o tubi.',
      'Disegna con la squadra un quadrato o rettangolo intorno al buco, 2–3 cm oltre la parte rotta, e taglialo con il seghetto.',
      'Taglia 2 listelli o profili 10 cm più lunghi dell\'apertura. Infilali dietro sui lati e fissali alla lastra esistente con 2 viti per lato.',
      'Taglia la toppa nuova dalla lastra della stessa misura del foro (meno 2 mm) e avvitala ai listelli ogni 15 cm, con le teste delle viti appena sotto la superficie senza rompere la carta.',
      'Stendi uno strato di stucco per giunti lungo le fughe, appoggia il nastro centrato sulla fuga e premilo con la spatola facendo uscire lo stucco in eccesso. Copri anche le teste delle viti.',
      'Dopo 24 h: seconda passata più larga (circa 15–20 cm) con la spatola grande.',
      'Dopo 24 h: passata sottile di stucco di finitura allargando ancora i bordi.',
      'Quando è asciutto leviga con grana 180 senza intaccare la carta del nastro, spolvera.',
      'Fissativo su tutta la riparazione, poi pittura (scheda F).'],
     ['Riempire il buco solo con stucco: si crepa e cade.', 'Mettere il nastro "a secco" senza stucco sotto: si stacca e fa bolle.', 'Levigare troppo fino a scoprire il nastro.', 'Pitturare senza fissativo: la toppa resta visibile sotto la pittura.'],
     'Stucco per giunti: 24 h tra le passate (12 h se a presa rapida, vedi confezione). Finitura: 12–24 h. Fissativo: 4–6 h prima della pittura.')

card('D. Buchi di viti e tasselli nel muro', 'Chiudere i fori in modo che non si vedano sotto la pittura',
     ['Stucco in pasta pronto (fori piccoli)', 'Stucco in polvere (fori grandi o profondi)', 'Intonaco premiscelato (fori oltre 2–3 cm di profondità)', 'Fissativo'],
     ['Pinza o cacciavite per estrarre i tasselli', 'Taglierino', 'Spatole 6 e 10 cm', 'Carta vetrata 180 + tampone', 'Pennellino'],
     ['Estrai viti e tasselli (con la pinza; se il tassello non esce, spingilo dentro di qualche millimetro).',
      'Allarga leggermente il bordo del foro con il taglierino a forma di cono, così lo stucco fa presa.',
      'Spolvera il foro e inumidiscilo con il pennellino bagnato.',
      'Fori profondi: prima riempi con stucco in polvere o intonaco, fino a 2–3 mm dalla superficie, e lascia indurire.',
      'Stendi lo stucco in pasta con la spatola incrociando due passate, lasciandone un velo in più rispetto al muro (lo stucco si ritira).',
      'Dopo l\'asciugatura, se si è formato un avvallamento, ripeti una passata sottile.',
      'Leviga con grana 180 a filo del muro e spolvera.',
      'Fissativo a pennello sui ritocchi, poi pittura (scheda F).'],
     ['Riempire un foro profondo in una sola passata di stucco in pasta: si ritira e si crepa.', 'Lasciare il tassello sporgente.', 'Pitturare senza fissativo: i ritocchi si vedono opachi.'],
     'Stucco in pasta: 2–24 h secondo lo spessore. Stucco in polvere: 30–60 min di lavorabilità, 4–24 h per levigare. Intonaco: 24 h.')

card('E. Buchi di viti nelle piastrelle del bagno', 'Chiudere i fori in modo pulito e impermeabile',
     ['Stucco epossidico bicomponente bianco o kit ripara-ceramica con smalto', 'Alcool denaturato', 'Nastro di carta', 'Stucco per fughe dello stesso colore (se i fori sono sulle fughe)'],
     ['Pinza', 'Spatolina in plastica o metallo', 'Stracci', 'Guanti in nitrile'],
     ['Estrai i tasselli; se si rompono, spingili dentro di 3–4 mm.',
      'Pulisci e sgrassa il foro e la piastrella intorno con l\'alcool; lascia asciugare.',
      'Metti il nastro di carta intorno al foro per proteggere lo smalto.',
      'Mescola i due componenti dello stucco epossidico nelle quantità indicate fino a colore uniforme.',
      'Riempi il foro con la spatolina, premendo bene, e livella a filo della piastrella.',
      'Togli subito il nastro e pulisci gli sbavi con lo straccio prima che indurisca.',
      'Dopo 24 h, se serve, ritocca con lo smalto bianco del kit.'],
     ['Usare stucco da muro o gesso sulle piastrelle: assorbe acqua e si sgretola.', 'Lasciare indurire gli sbavi epossidici: dopo non si tolgono più.', 'Bagnare la zona prima di 24 h.'],
     'Lavorabilità epossidico: 10–30 min. Indurimento: 24 h. Il colore non sarà identico alla piastrella: se i fori sono vicini alle fughe, chiudili lì con lo stucco per fughe.')

card('F. Pittura bianca tutta casa', 'Due mani uniformi su soffitti e pareti',
     ['Fissativo all\'acqua', 'Pittura bianca per prima mano (o lavabile diluita)', 'Pittura bianca lavabile traspirante (finitura)', 'Pittura antimuffa per cucina e bagno', 'Nastro di carta, teli'],
     ['Rullo pelo medio 22–25 cm + prolunga', 'Pennello piatto 5 cm e pennellino', 'Vaschetta con griglia', 'Scala o trabattello', 'Secchio d\'acqua per lavare gli attrezzi'],
     ['Svuota o raccogli i mobili al centro e coprili. Copri il pavimento. Smonta o copri placche e interruttori (corrente staccata).',
      'Nastro di carta su battiscopa, infissi, piastrelle e bordi.',
      'Spolvera le pareti; lava le macchie di grasso in cucina con acqua e sgrassatore neutro e risciacqua.',
      'Fissativo diluito con acqua come da scheda tecnica (di solito 1 parte di prodotto e 4–5 di acqua) su rasature, stucchi, cartongesso e muri che spolverano. Asciugatura 4–6 h.',
      'Mescola bene la pittura. Diluisci come da etichetta (indicativo: 1ª mano 20–25% di acqua, 2ª mano 10–15%).',
      'Ordine: prima il soffitto, poi le pareti, dall\'alto verso il basso. Inizia dal lato della finestra.',
      'Con il pennello "ritaglia" angoli, bordi del soffitto, intorno a porte, finestre e prese (una fascia di 5 cm).',
      'Con il rullo stendi a "W" su zone di circa 1 m², poi uniforma con passate verticali senza ricaricare. Lavora "fresco su fresco" per non lasciare segni.',
      'Prima mano su tutta la stanza; aspetta 4–6 h (come da etichetta).',
      'Seconda mano con le stesse modalità. In cucina e in bagno usa la pittura antimuffa.',
      'Togli il nastro di carta quando la seconda mano è ancora appena fresca, tirandolo a 45°.',
      'Rimonta placche e interruttori, arieggia la casa per 24–48 h.'],
     ['Pitturare con meno di +5 °C o al sole diretto.', 'Ricaricare il rullo a metà di una zona già stesa: restano aloni.', 'Fermarsi a metà parete: si vede la ripresa.', 'Togliere il nastro a pittura secca: strappa il bordo.', 'Usare lotti diversi di pittura sulla stessa parete senza mescolarli prima.'],
     'Fissativo: 4–6 h. Tra le mani: 4–6 h. Asciutta al tatto: 1–2 h; completamente indurita: 2–3 settimane (non lavare le pareti prima).')

# =====================================================================================
# 6. DRYING TABLE + NOTES
new_page('Tempi di asciugatura', 'Valori indicativi a 20 °C con umidità normale — vale sempre la scheda tecnica del prodotto')
TT = [('Antimuffa', '15–30 min di posa · ripetere dopo 24 h'), ('Aggrappante per cemento', '2–4 h'), ('Intonaco premiscelato', '24 h per cm di spessore'),
      ('Rasante (tra le mani)', '24–48 h'), ('Rasante prima della pittura', '3–7 giorni'), ('Stucco per giunti cartongesso', '12–24 h tra le passate'),
      ('Stucco in pasta', '2–24 h secondo lo spessore'), ('Stucco in polvere', '4–24 h'), ('Stucco epossidico (piastrelle)', '24 h'),
      ('Fissativo', '4–6 h'), ('Pittura (tra 1ª e 2ª mano)', '4–6 h'), ('Pittura completamente indurita', '2–3 settimane')]
for a, b in TT:
    need(20); y = st['y']
    c.setFillColor(BAND); c.rect(M, y - 16, W - 2 * M, 16, fill=1, stroke=0)
    c.setFont('DVB', 9); c.setFillColor(INK); c.drawString(M + 8, y - 11, a)
    c.setFont('DV', 9); c.drawString(M + 230, y - 11, b)
    st['y'] -= 19
st['y'] -= 10
band('Note (colori scelti, negozi, date, problemi riscontrati)', size=10)
h = st['y'] - 52
field('note_finali', M, 52, W - 2 * M, h, multiline=True, size=9)
c.save()
print('ok', OUT, 'pages', st['page'], 'fields', st['fid'])
