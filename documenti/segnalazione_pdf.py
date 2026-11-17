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
FOTO = [(sys.argv[2] + '/01_cucina_vista.jpg', 'Foto 1 – Cucina, vista generale', 'Muri che danno sull\'esterno: muffa nera nella fascia bassa, negli angoli e dove c\'erano i mobili.'),
        (sys.argv[2] + '/02_cucina_attacchi_acqua.jpg', 'Foto 2 – Cucina, zona attacchi acqua e gas', 'Muro esterno: muffa intorno agli attacchi; parquet annerito e doghe che si staccano vicino al muro.'),
        (sys.argv[2] + '/03_stanza_muro_verde.jpg', 'Foto 3 – Camera, muro esterno', 'Muro che dà sull\'esterno: macchie di muffa diffuse fino a circa 1 m di altezza.'),
        (sys.argv[2] + '/04_stanza_angolo_zoccolo.jpg', 'Foto 4 – Camera, angolo tra due muri esterni', 'Muffa lungo lo zoccolo e nell\'angolo tra i due muri che danno sull\'esterno.')]
def head(p):
    c.setFillColor(ACC); c.rect(0, H - 60, W, 60, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('DVB', 15); c.drawString(M, H - 32, 'Allegato fotografico – muffa e umidità')
    c.setFont('DV', 8.5); c.drawString(M, H - 48, 'Condominio Monte Bianco, Via Monte Zebio 23/27, Thiene – unità al piano terra [scala/interno]')
    if p == 1:
        c.setFillColor(HexColor('#a3402f')); c.setFont('DVB', 9); c.drawString(M, H - 76, 'Tutti i muri fotografati sono muri perimetrali che danno sull\'esterno dell\'edificio.')
    c.setFillColor(MUTED); c.setFont('DV', 7.5); c.drawString(M, 22, 'Data delle foto: ' + (sys.argv[3] if len(sys.argv) > 3 else '____________')); c.drawRightString(W - M, 22, f'Pagina {p}')
for p in range(2):
    head(p + 1); y = H - 90
    for path, title, desc in FOTO[p * 2:p * 2 + 2]:
        img = ImageReader(path); iw, ih = img.getSize(); bw, bh = W - 2 * M, 300; s = min(bw / iw, bh / ih)
        w, h = iw * s, ih * s
        c.drawImage(img, M + (bw - w) / 2, y - h, w, h)
        c.setFillColor(INK); c.setFont('DVB', 10); c.drawString(M, y - h - 16, title)
        c.setFillColor(MUTED); c.setFont('DV', 8.5); c.drawString(M, y - h - 29, desc)
        y -= h + 48
    c.showPage()
c.save(); print('ok')
