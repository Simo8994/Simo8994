"""Allegato fotografico per l'amministratore. python3 segnalazione_pdf.py out.pdf cartella_foto"""
import sys, datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
pdfmetrics.registerFont(TTFont('DV', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
W, H = A4; M = 42; ACC = HexColor('#7d6246'); INK = HexColor('#2b2622'); MUTED = HexColor('#7a716a')
c = canvas.Canvas(sys.argv[1], pagesize=A4); c.setTitle('Allegato fotografico - muffa e umidita')
FOTO = [(sys.argv[2] + '/01_cucina_vista.jpg', 'Foto 1 – Cucina, vista generale', 'Muffa nera nella fascia bassa dei muri esterni, negli angoli e dove c\'erano i mobili.'),
        (sys.argv[2] + '/02_cucina_attacchi_acqua.jpg', 'Foto 2 – Cucina, zona attacchi acqua e gas', 'Muffa concentrata intorno agli attacchi; parquet annerito e doghe che si staccano vicino al muro.'),
        (sys.argv[2] + '/03_stanza_muro_verde.jpg', 'Foto 3 – [Nome stanza], muro esterno', 'Macchie di muffa diffuse fino a circa 1 m di altezza, più scure nell\'angolo.'),
        (sys.argv[2] + '/04_stanza_angolo_zoccolo.jpg', 'Foto 4 – [Nome stanza], angolo e zoccolo', 'Muffa lungo lo zoccolo e nell\'angolo tra i due muri esterni.')]
def head(p):
    c.setFillColor(ACC); c.rect(0, H - 60, W, 60, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('DVB', 15); c.drawString(M, H - 32, 'Allegato fotografico – muffa e umidità')
    c.setFont('DV', 8.5); c.drawString(M, H - 48, 'Condominio Monte Bianco, Via Monte Zebio 23/27, Thiene – unità al piano terra [scala/interno]')
    c.setFillColor(MUTED); c.setFont('DV', 7.5); c.drawString(M, 22, 'Data delle foto: ____________'); c.drawRightString(W - M, 22, f'Pagina {p}')
for p in range(2):
    head(p + 1); y = H - 80
    for path, title, desc in FOTO[p * 2:p * 2 + 2]:
        img = ImageReader(path); iw, ih = img.getSize(); bw, bh = W - 2 * M, 300; s = min(bw / iw, bh / ih)
        w, h = iw * s, ih * s
        c.drawImage(img, M + (bw - w) / 2, y - h, w, h)
        c.setFillColor(INK); c.setFont('DVB', 10); c.drawString(M, y - h - 16, title)
        c.setFillColor(MUTED); c.setFont('DV', 8.5); c.drawString(M, y - h - 29, desc)
        y -= h + 48
    c.showPage()
c.save(); print('ok')
