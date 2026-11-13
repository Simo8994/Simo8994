"""Editable PDF (AcroForm): shopping list with tick boxes + quantity/notes fields, then step-by-step instructions."""
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
M = 40
ACC = HexColor('#8a6d4b'); INK = HexColor('#2b2622'); MUTED = HexColor('#7a716a'); LINE = HexColor('#d9d2c8'); BAND = HexColor('#f3eee7')

LISTA = [
    ('1. Muffa e umidità (mezza parete cucina)', [
        ('Antimuffa igienizzante (spray o liquido)', '1 L'),
        ('Spugne e stracci per la muffa', ''),
        ('Guanti in nitrile + occhiali', ''),
        ('Rasante deumidificante / traspirante a calce', '1–2 sacchi'),
        ('Pittura antimuffa traspirante bianca (cucina e bagno)', '2,5–5 L'),
    ]),
    ('2. Rasatura muro interno', [
        ('Aggrappante per cemento (solo se cemento liscio)', ''),
        ('Intonaco bianco premiscelato per interni', ''),
        ('Rasante-collante fine per interni', '1,2–1,5 kg/m² per mano'),
        ('Rete in fibra di vetro per rasatura', ''),
    ]),
    ('3. Buchi grandi nel cartongesso', [
        ('Lastra cartongesso 12,5 mm (anche mezza)', '1'),
        ('Profilo metallico o listelli di legno di rinforzo', ''),
        ('Viti autoperforanti per cartongesso 25 mm', ''),
        ('Nastro per giunti in carta microforata', ''),
        ('Stucco per giunti + stucco di finitura (o unico)', ''),
        ('Seghetto per cartongesso', ''),
    ]),
    ('4. Buchi di viti nel muro', [
        ('Stucco in pasta pronto (buchi piccoli)', ''),
        ('Stucco in polvere (buchi grandi/profondi)', ''),
    ]),
    ('5. Buchi di viti nelle piastrelle del bagno', [
        ('Stucco epossidico bicomponente bianco / kit ripara-ceramica', ''),
        ('Nastro di carta', ''),
        ('Alcool per sgrassare', ''),
    ]),
    ('6. Pittura bianca tutta casa', [
        ('Fissativo all\'acqua', '1 L ogni 10–15 m²'),
        ('Pittura bianca lavabile traspirante', '1 L ogni 10 m² × 2 mani'),
        ('Rullo pelo medio + prolunga', ''),
        ('Pennello piatto 5 cm', ''),
        ('Vaschetta con griglia', ''),
        ('Nastro di carta', ''),
        ('Teli / carta per il pavimento', ''),
    ]),
    ('7. Attrezzi', [
        ('Cazzuola americana sottile inox 28–32 cm', ''),
        ('Spatole inox 6 / 10 / 20 cm', ''),
        ('Frattazzino in spugna grana fine', ''),
        ('Spugna per rasare', ''),
        ('Secchi da muratore + frusta per trapano', '2'),
        ('Livella laser', ''),
        ('Taglierino + lame di ricambio', ''),
        ('Dischi per mola da muro', ''),
    ]),
    ('8. Levigatura', [
        ('Dischi levigatrice grana 120 e 180', ''),
        ('Sacco in tessuto per levigatrice', ''),
        ('Carta vetrata a mano 120 / 180 + tampone', ''),
    ]),
    ('9. Protezione e pulizia', [
        ('Mascherine FFP2/FFP3 con filtri', ''),
        ('Teli e sacchi copri-mobili', ''),
        ('Guanti da lavoro', ''),
    ]),
]

ISTR = [
    ('Ordine generale', ['Proteggi la casa → tratta la muffa → ripara (cartongesso, buchi, intonaco) → rasa → leviga → fissativo → pittura.']),
    ('1. Mezza parete cucina con umidità', [
        'Trova la causa: muffa solo d\'inverno, negli angoli e dietro i mobili = condensa (arieggia, antimuffa, pittura antimuffa). Muro bagnato dal basso o vicino al lavello = risalita o perdita: fai controllare idraulico e muro.',
        'Spruzza l\'antimuffa, lascia agire 15–30 min, strofina. Ripeti dopo 24 h se serve.',
        'Togli con la spatola l\'intonaco che si sbriciola o suona vuoto.',
        'Lascia asciugare bene il muro per qualche giorno, arieggiando.',
        'Rasa con il rasante traspirante in 2 mani (vedi punto 2).',
        'Fissativo e pittura antimuffa.',
        'ATTENZIONE: non mescolare mai antimuffa e candeggina; stanza sempre aerata.',
    ]),
    ('2. Rasatura muro interno', [
        'Togli polvere e parti che si staccano, poi bagna leggermente il muro.',
        'Se il muro è cemento liscio: aggrappante, asciugatura 2–4 h.',
        'Riempi buchi e tracce profonde con l\'intonaco, asciugatura 24 h.',
        'Prima mano di rasante 2–3 mm; se ci sono crepe annega la rete nel rasante fresco.',
        'Aspetta 24–48 h, poi carta vetrata sulle creste.',
        'Seconda mano sottile 1–2 mm; quando è soda al tatto (5–15 min rasante fine, 15–40 min cementizio) passa il frattazzino inumidito con movimenti circolari.',
        'Lascia asciugare 3–7 giorni prima di pitturare.',
    ]),
    ('3. Buchi grandi nel cartongesso', [
        'Ritaglia il buco a quadrato o rettangolo regolare con il seghetto.',
        'Infila dietro 2 listelli o profili e fissali con le viti alla lastra esistente.',
        'Taglia un pezzo di cartongesso della stessa misura e avvitalo ai listelli, teste delle viti appena sotto la superficie.',
        'Lungo i bordi stucco per giunti, appoggia il nastro e schiaccialo con la spatola.',
        'Dopo 24 h seconda passata più larga (circa 20 cm per lato).',
        'Asciutto: stucco di finitura sottile, leviga grana 180, spolvera.',
        'Fissativo e pittura.',
    ]),
    ('4. Buchi di viti nel muro', [
        'Togli tasselli e viti, allarga leggermente il buco con il taglierino.',
        'Spolvera e inumidisci il buco.',
        'Riempi con lo stucco (pasta per i piccoli, polvere per i grandi), lasciandone un po\' in più.',
        'Buchi profondi: 2 passate a qualche ora di distanza, perché lo stucco si ritira.',
        'Leviga grana 180 a filo del muro, poi fissativo e pittura.',
    ]),
    ('5. Buchi di viti nelle piastrelle del bagno', [
        'Togli i tasselli e pulisci il buco con l\'alcool.',
        'Nastro di carta intorno al buco.',
        'Mescola lo stucco epossidico, riempi e liscia a filo con la spatola; togli subito il nastro.',
        'Lascia indurire 24 h; se serve ritocca con lo smalto bianco.',
        'Il colore non sarà identico alla piastrella; se i buchi sono vicini alle fughe usa lo stucco per fughe dello stesso colore.',
    ]),
    ('6. Pittura bianca tutta casa', [
        'Svuota o copri i mobili, copri il pavimento, nastro di carta su battiscopa, infissi e prese.',
        'Su rasature, stucchi e cartongesso nuovi: fissativo diluito come da confezione, asciugatura 4–6 h.',
        'Prima il soffitto, poi le pareti: pennello negli angoli e lungo i bordi, poi rullo a "W" e passate verticali.',
        'Prima mano, attendi 4–6 h, seconda mano.',
        'In cucina e in bagno usa la pittura antimuffa.',
        'Togli il nastro quando la pittura è ancora appena fresca, per un bordo netto.',
    ]),
]

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle('Lista lavori e spesa casa'); c.setAuthor('Lista lavori')
form = c.acroForm
page = [1]

def header(title, sub):
    c.setFillColor(ACC); c.rect(0, H - 70, W, 70, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('DVB', 18); c.drawString(M, H - 38, title)
    c.setFont('DV', 9.5); c.drawString(M, H - 56, sub)
    c.setFillColor(MUTED); c.setFont('DV', 8); c.drawRightString(W - M, 22, f'Pagina {page[0]}')

def new_page(title, sub):
    c.showPage(); page[0] += 1; header(title, sub); return H - 95

def wrap(text, font, size, width):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

# ---------- shopping list ----------
header('Lista della spesa — lavori casa', 'Spunta ✓ quello che hai comprato, scrivi quantità e note. Campi modificabili.')
y = H - 95
c.setFont('DV', 8); c.setFillColor(MUTED)
c.drawString(M + 4, y, 'Preso'); c.drawString(M + 40, y, 'Materiale'); c.drawString(W - M - 215, y, 'Quantità'); c.drawString(W - M - 110, y, 'Note / negozio / €')
y -= 10
fid = 0
for cat, items in LISTA:
    need = 26 + 20 * len(items)
    if y - need < 50: y = new_page('Lista della spesa — lavori casa', 'continua')
    c.setFillColor(BAND); c.rect(M, y - 18, W - 2 * M, 18, fill=1, stroke=0)
    c.setFillColor(ACC); c.setFont('DVB', 10.5); c.drawString(M + 6, y - 13, cat)
    y -= 24
    for name, qty in items:
        fid += 1
        form.checkbox(name=f'preso_{fid}', x=M + 6, y=y - 12, size=12, borderColor=ACC, fillColor=white, buttonStyle='check', borderWidth=1, forceBorder=True)
        c.setFillColor(INK); c.setFont('DV', 9); c.drawString(M + 26, y - 9, name)
        form.textfield(name=f'qta_{fid}', value=qty.replace('–', '-').replace('²', '2').replace('×', 'x'), x=W - M - 215, y=y - 14, width=100, height=15, fontName='Helvetica', fontSize=8, borderColor=LINE, fillColor=white, textColor=INK, borderWidth=0.6, forceBorder=True)
        form.textfield(name=f'note_{fid}', value='', x=W - M - 110, y=y - 14, width=110, height=15, fontName='Helvetica', fontSize=8, borderColor=LINE, fillColor=white, textColor=INK, borderWidth=0.6, forceBorder=True)
        y -= 20
    y -= 6
# extra free rows
if y < 160: y = new_page('Lista della spesa — lavori casa', 'continua')
c.setFillColor(BAND); c.rect(M, y - 18, W - 2 * M, 18, fill=1, stroke=0)
c.setFillColor(ACC); c.setFont('DVB', 10.5); c.drawString(M + 6, y - 13, 'Altro (righe libere)')
y -= 24
for k in range(5):
    fid += 1
    form.checkbox(name=f'preso_{fid}', x=M + 6, y=y - 12, size=12, borderColor=ACC, fillColor=white, buttonStyle='check', borderWidth=1, forceBorder=True)
    form.textfield(name=f'voce_{fid}', value='', x=M + 26, y=y - 14, width=W - 2 * M - 250, height=15, fontName='Helvetica', fontSize=8, borderColor=LINE, fillColor=white, borderWidth=0.6, forceBorder=True)
    form.textfield(name=f'qta_{fid}', value='', x=W - M - 215, y=y - 14, width=100, height=15, fontName='Helvetica', fontSize=8, borderColor=LINE, fillColor=white, borderWidth=0.6, forceBorder=True)
    form.textfield(name=f'note_{fid}', value='', x=W - M - 110, y=y - 14, width=110, height=15, fontName='Helvetica', fontSize=8, borderColor=LINE, fillColor=white, borderWidth=0.6, forceBorder=True)
    y -= 20

# ---------- instructions ----------
y = new_page('Istruzioni passo passo', 'Spunta ✓ ogni passaggio fatto. In fondo ci sono le note libere.')
for title, steps in ISTR:
    lines_needed = sum(len(wrap(s, 'DV', 9, W - 2 * M - 40)) for s in steps)
    if y - (26 + lines_needed * 12 + len(steps) * 5) < 50: y = new_page('Istruzioni passo passo', 'continua')
    c.setFillColor(BAND); c.rect(M, y - 18, W - 2 * M, 18, fill=1, stroke=0)
    c.setFillColor(ACC); c.setFont('DVB', 10.5); c.drawString(M + 6, y - 13, title)
    y -= 26
    for i, s in enumerate(steps):
        fid += 1
        lines = wrap(s, 'DV', 9, W - 2 * M - 40)
        warn = s.startswith('ATTENZIONE')
        form.checkbox(name=f'fatto_{fid}', x=M + 6, y=y - 10, size=11, borderColor=ACC, fillColor=white, buttonStyle='check', borderWidth=1, forceBorder=True)
        c.setFont('DVB' if warn else 'DV', 9); c.setFillColor(HexColor('#a3402f') if warn else INK)
        for j, ln in enumerate(lines):
            c.drawString(M + 26, y - 8 - j * 12, ln)
        y -= len(lines) * 12 + 5
    y -= 8

if y < 200: y = new_page('Note', '')
c.setFillColor(BAND); c.rect(M, y - 18, W - 2 * M, 18, fill=1, stroke=0)
c.setFillColor(ACC); c.setFont('DVB', 10.5); c.drawString(M + 6, y - 13, 'Note (metri quadri, colori scelti, tempi)')
form.textfield(name='note_finali', value='', x=M, y=60, width=W - 2 * M, height=y - 30 - 60, fontName='Helvetica', fontSize=9,
               borderColor=LINE, fillColor=white, borderWidth=0.6, forceBorder=True, fieldFlags='multiline')
c.save()
print('ok', OUT, 'pages', page[0])
