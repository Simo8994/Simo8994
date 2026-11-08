#!/usr/bin/env python3
"""Scrive testi-pubblicazione.md (IT + EN) per ogni storia definita in storie.py."""
from storie import RADICE, STORIE

HASHTAG = {
    "02-guerra-degli-emu": ("#australia #emù", "#australia #emuwar"),
    "03-secchia-rapita": ("#modena #bologna #medioevo", "#italy #medieval"),
    "04-onoda": ("#giappone #secondaguerramondiale", "#japan #ww2"),
    "05-onda-di-melassa": ("#boston #disastri", "#boston #disaster"),
    "06-peste-del-ballo": ("#misteri #medioevo", "#mystery #medieval"),
    "07-phineas-gage": ("#cervello #scienza", "#brain #science"),
    "08-stanislav-petrov": ("#guerrafredda #nucleare", "#coldwar #nuclear"),
    "09-ponte-di-tacoma": ("#ingegneria #ponti", "#engineering #bridge"),
    "10-grande-puzza": ("#londra #ottocento", "#london #victorian"),
}
TITOLI_BRANI = {
    "Five-Armies.mp3": "Five Armies", "Volatile-Reaction.mp3": "Volatile Reaction",
    "Hitman.mp3": "Hitman", "Darkest-Child.mp3": "Darkest Child",
    "Curse-of-the-Scarab.mp3": "Curse of the Scarab",
    "Monkeys-Spinning-Monkeys.mp3": "Monkeys Spinning Monkeys",
}


def testo(t):
    return t[0] if isinstance(t, tuple) else t


def main():
    for nome, s in STORIE.items():
        slug = nome.split("-", 1)[1]
        aggancio_it, aggancio_en = testo(s["scene"][0][3]), testo(s["scene"][0][4])
        h_it, h_en = HASHTAG.get(nome, ("", ""))
        brano = TITOLI_BRANI[s["musica"]]
        credito = (f'Music: "{brano}" by Kevin MacLeod (incompetech.com)\n'
                   "Licensed under Creative Commons: By Attribution 4.0\n"
                   "http://creativecommons.org/licenses/by/4.0/")
        md = f"""# {s['titolo'][1].title()} – {s['titolo'][0].title()}

## 🇮🇹 ITALIANO – `{slug}.mp4`

### YouTube Shorts
**Titolo:** {aggancio_it} #shorts
**Descrizione:**
{aggancio_it}
Iscriviti per altre storie che a scuola non ti raccontano.
#storia #curiosità {h_it} #shorts

{credito}

### TikTok
{aggancio_it} 😳 #storia #curiosità #imparacontiktok {h_it}

### Instagram Reels
{aggancio_it} 😳
Salvalo e mandalo a chi ama la storia.
.
#storia #curiosità #reels {h_it}

---

## 🇬🇧 ENGLISH – `{slug}-EN.mp4`

### YouTube Shorts
**Title:** {aggancio_en} #shorts
**Description:**
{aggancio_en}
Subscribe for more insane history.
#history #historyfacts {h_en} #shorts

{credito}

### TikTok
{aggancio_en} 😳 #history #historytok #facts {h_en}

### Instagram Reels
{aggancio_en} 😳
Save this and send it to a history lover.
.
#history #didyouknow #reels {h_en}
"""
        (RADICE / nome / "testi-pubblicazione.md").write_text(md, encoding="utf-8")
        print("scritto", nome)


if __name__ == "__main__":
    main()
