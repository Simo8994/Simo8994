#!/usr/bin/env python3
"""Definizione compatta delle storie -> video/NN-nome/scene.json (IT + EN).

Ogni storia: titolo IT/EN, musica, immagini (chiave -> prompt), scene.
Scena: (immagine, ritaglio|None, effetti, testo_it, testo_en)
  - testo puo' essere una stringa o (testo_a_schermo, testo_parlato)
  - immagine: chiave del dizionario "immagini" oppure percorso "archivio/..."

    python3 strumenti/storie.py      # scrive/aggiorna tutti gli scene.json
"""
import json
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent / "video"
CTA = ("Seguimi per altre storie assurde.", "Follow for more insane history.")
Z1, Z2, Z3 = [0.15, 0.1, 0.7, 0.7], [0.1, 0.35, 0.7, 0.6], [0.25, 0.2, 0.6, 0.6]

STORIE = {
    "02-guerra-degli-emu": dict(
        titolo=("EMÙ 1 · ESERCITO 0", "LA GUERRA DEGLI EMÙ"), titolo_en=("EMUS 1 · ARMY 0", "THE GREAT EMU WAR"),
        musica="Monkeys-Spinning-Monkeys.mp3",
        evidenzia=["emù", "perse", "ritirò", "carri"], evidenzia_en=["emus", "lost", "tanks"],
        immagini={
            "a": "close-up of several big emu birds with long necks standing in a golden wheat field, staring at the viewer, Western Australia, 1932",
            "b": "1930s Western Australian wheat farm, wide dry landscape, farmhouse, golden wheat",
            "c": "three middle-aged 1930s australian male farmers with hats and moustaches standing by a wheat field, worried",
            "d": "1930s australian soldiers in khaki uniforms with a machine gun on a tripod in a field",
            "e": "dozens of emus running away in a dusty field, motion blur, chaos",
            "f": "1930s army truck driving through dust in the australian outback",
        },
        scene=[
            ("a", None, ["boom", "flash"], "Nel 1932 l'esercito australiano dichiarò guerra agli emù. E perse.",
             "In 1932, the Australian army declared war on emus. And lost."),
            ("b", None, [], "Ventimila emù stavano devastando i campi di grano.",
             "Twenty thousand emus were destroying the wheat fields."),
            ("c", None, [], "Gli agricoltori, molti ex soldati, chiesero aiuto al governo.",
             "The farmers, many of them ex-soldiers, asked the government for help."),
            ("d", None, [], "Arrivarono un maggiore, due soldati, due mitragliatrici e diecimila proiettili.",
             "The army sent a major, two soldiers, two machine guns and ten thousand rounds."),
            ("a", Z1, [], "Sembrava una passeggiata.", "It looked easy."),
            ("e", None, ["boom", "scossa"], "Ma al primo sparo, gli emù si divisero in piccoli gruppi e scapparono ovunque.",
             "But at the first shot, the emus split into small groups and ran in every direction."),
            ("f", None, [], "I camion non riuscivano a inseguirli. Una mitragliatrice si inceppò.",
             "The trucks couldn't keep up. One machine gun jammed."),
            ("d", Z3, [], "Dopo pochi giorni, l'esercito si ritirò.", "After a few days, the army pulled out."),
            ("e", Z2, [], "Il maggiore disse che gli emù affrontavano le mitragliatrici come carri armati.",
             "The major said the emus could face machine guns like tanks."),
            ("b", Z3, [], "Ci riprovarono. Alla fine: quasi diecimila colpi per circa mille emù.",
             "They tried again. Final count: almost ten thousand rounds for about a thousand emus."),
            ("a", Z2, [], "E gli emù? Sono ancora lì.", "And the emus? Still there."),
            ("a", Z3, [], *CTA),
        ]),
    "03-secchia-rapita": dict(
        titolo=("LA GUERRA DEL SECCHIO", "MODENA CONTRO BOLOGNA"), titolo_en=("THE BUCKET WAR", "MODENA VS BOLOGNA"),
        musica="Five-Armies.mp3",
        evidenzia=["secchio", "modena", "bologna", "trofeo"], evidenzia_en=["bucket", "modena", "bologna", "trophy"],
        immagini={
            "a": "huge medieval battle, knights on horses clashing in italian countryside, 14th century, banners",
            "b": "medieval italian city with tall stone towers and red brick walls, Bologna, 14th century",
            "c": "medieval soldiers sneaking at night near a stone well in an italian town square, moonlight",
            "d": "an old wooden bucket hanging over a stone well, medieval, close-up",
            "e": "medieval army of thousands of soldiers with flags on a hill at dawn, italy",
            "f": "medieval knights chasing fleeing soldiers toward city gates, dust, chaos",
        },
        scene=[
            ("a", None, ["boom", "flash"], "Una delle più grandi battaglie del Medioevo… per un secchio.",
             "One of the biggest battles of the Middle Ages… over a bucket."),
            ("b", None, [], "Italia, 1325. Modena contro Bologna.", "Italy, 1325. Modena versus Bologna."),
            ("b", Z3, [], "Le due città si odiano da anni: guelfi contro ghibellini.",
             "The two cities have hated each other for years."),
            ("c", None, [], "Secondo la leggenda, i soldati di Modena entrano a Bologna e rubano… un secchio di legno.",
             "Legend says Modena's soldiers sneaked into Bologna and stole… a wooden bucket."),
            ("d", None, [], "Bologna non la prende bene.", "Bologna did not take it well."),
            ("e", None, [], "A Zappolino si scontrano circa trentamila bolognesi contro settemila modenesi.",
             "At Zappolino, about thirty thousand men from Bologna faced seven thousand from Modena."),
            ("a", Z1, ["boom", "scossa"], "Sembra già scritta. E invece vince Modena.",
             "It looked decided. Instead, Modena won."),
            ("f", None, [], "I modenesi inseguono i nemici fino alle porte di Bologna.",
             "Modena chased the enemy right up to the gates of Bologna."),
            ("d", Z3, [], "E come trofeo si portano a casa… il secchio.", "And as a trophy, they took home… the bucket."),
            ("b", Z2, [], "Quel secchio è ancora oggi a Modena.", "That bucket is still in Modena today."),
            ("e", Z3, [], *CTA),
        ]),
    "04-onoda": dict(
        titolo=("29 ANNI", "DI GUERRA IN PIÙ"), titolo_en=("29 YEARS", "OF EXTRA WAR"),
        musica="Hitman.mp3",
        evidenzia=["29", "arrenderti", "propaganda", "comandante"], evidenzia_en=["29", "surrender", "propaganda", "commander"],
        immagini={
            "a": "japanese world war two soldier in tattered uniform with rifle hiding in dense tropical jungle",
            "b": "tropical island covered in jungle, philippines, 1940s, misty mountains, sea",
            "c": "paper leaflets falling from the sky over a dense jungle",
            "d": "lonely soldier sitting by a small fire in a jungle at night, worn uniform",
            "e": "1970s young japanese traveler with backpack in a jungle clearing",
            "f": "elderly japanese officer in uniform reading an order in a jungle, solemn",
        },
        scene=[
            ("a", None, ["boom", "flash"], "Questo soldato ha combattuto la Seconda guerra mondiale per 29 anni dopo la fine.",
             "This soldier kept fighting World War Two for 29 years after it ended."),
            ("b", None, [], "Filippine, 1944. Il tenente Hiroo Onoda viene mandato sull'isola di Lubang.",
             "Philippines, 1944. Lieutenant Hiroo Onoda is sent to Lubang Island."),
            ("a", Z1, [], "L'ordine è chiaro: non arrenderti mai.", "His orders: never surrender."),
            ("b", Z3, [], "Nel 1945 la guerra finisce. Ma lui non ci crede.", "In 1945 the war ends. He doesn't believe it."),
            ("c", None, [], "Volantini, giornali, lettere della famiglia: per lui è tutta propaganda nemica.",
             "Leaflets, newspapers, letters from his family: he thinks it's all enemy propaganda."),
            ("d", None, [], "Passano gli anni. I suoi compagni muoiono o si arrendono. Lui resta nella giungla.",
             "Years pass. His comrades die or surrender. He stays in the jungle."),
            ("a", Z2, [], "Ma non fu un eroe per tutti: negli scontri morirono anche diversi abitanti dell'isola.",
             "But he was no hero to everyone: several islanders were killed in his raids."),
            ("e", None, [], "Nel 1974 un giovane viaggiatore giapponese lo trova.", "In 1974, a young Japanese traveler finds him."),
            ("d", Z3, [], "Onoda si arrende a una sola condizione: l'ordine deve arrivare dal suo vecchio comandante.",
             "Onoda will surrender on one condition: the order must come from his old commander."),
            ("f", None, ["flash"], "Il comandante vola sull'isola. E gli ordina di deporre le armi.",
             "The commander flies to the island and orders him to lay down his arms."),
            ("b", Z2, [], "Ventinove anni dopo, la sua guerra è finita.", "Twenty-nine years later, his war is finally over."),
            ("a", Z3, [], *CTA),
        ]),
    "05-onda-di-melassa": dict(
        titolo=("ONDA DI MELASSA", "BOSTON 1919"), titolo_en=("MOLASSES WAVE", "BOSTON 1919"),
        musica="Volatile-Reaction.mp3",
        evidenzia=["melassa", "esplode", "ventuno"], evidenzia_en=["molasses", "bursts", "twenty-one"],
        immagini={
            "a": "giant brown wave of thick molasses flooding a 1919 Boston street, buildings, people running",
            "b": "1919 Boston North End street with elevated railway, horse carts, people, winter",
            "c": "huge cylindrical steel storage tank next to a harbor, 1919, cold winter day",
            "d": "giant steel tank bursting open, brown liquid exploding out, rivets flying",
            "e": "horse-drawn wagon stuck in thick brown syrup in a street, 1919",
            "f": "1919 firefighters cleaning a brown sticky street with water hoses",
        },
        scene=[
            ("a", None, ["boom", "flash"], "Nel 1919 un'onda alta sette metri travolse Boston. Era fatta di melassa.",
             "In 1919, a wave twenty-five feet high swept through Boston. It was made of molasses."),
            ("b", None, [], ("15 gennaio 1919. Quartiere di North End.", "Quindici gennaio, millenovecentodiciannove. Quartiere di North End."),
             "January 15, 1919. Boston's North End."),
            ("c", None, [], "Un enorme serbatoio contiene quasi nove milioni di litri di melassa.",
             "A giant tank holds over two million gallons of molasses."),
            ("d", None, ["boom", "flash", "scossa"], "All'improvviso, il serbatoio esplode.", "Suddenly, the tank bursts."),
            ("a", Z1, [], "Un'onda appiccicosa corre per le strade a oltre cinquanta chilometri all'ora.",
             "A sticky wave races down the streets at thirty-five miles per hour."),
            ("e", None, [], "Travolge case, carri, cavalli e persone.", "It crushes houses, wagons, horses and people."),
            ("e", Z3, [], "Più si cerca di uscirne, più si resta intrappolati.", "The more people struggle, the more they get stuck."),
            ("b", Z3, [], "Muoiono ventuno persone. Oltre centocinquanta i feriti.",
             "Twenty-one people die. About a hundred and fifty are injured."),
            ("f", None, [], "Per ripulire servirono settimane, e acqua di mare.", "The cleanup took weeks, using seawater."),
            ("b", Z2, [], "Si racconta che per decenni, nei giorni caldi, il quartiere profumasse ancora di melassa.",
             "Locals said that for decades, on hot days, the neighborhood still smelled of molasses."),
            ("a", Z3, [], *CTA),
        ]),
    "06-peste-del-ballo": dict(
        titolo=("LA PESTE DEL BALLO", "STRASBURGO 1518"), titolo_en=("THE DANCING PLAGUE", "STRASBOURG 1518"),
        musica="Darkest-Child.mp3",
        evidenzia=["ballare", "centinaia", "ballo"], evidenzia_en=["dancing", "hundreds", "dance"],
        immagini={
            "a": "crowd of people dancing frantically in a medieval cobblestone street, 1518, eerie, exhausted faces",
            "b": "medieval Strasbourg town with gothic cathedral spire, half-timbered houses, summer",
            "c": "a woman in 16th century peasant dress dancing alone in an empty cobblestone street",
            "d": "medieval musicians with drums, pipes and lutes playing on a wooden stage in a town square",
            "e": "exhausted medieval people collapsed on the ground in a street, dramatic shadows",
            "f": "medieval town council of nobles in robes discussing in a dark hall",
        },
        scene=[
            ("a", None, ["boom", "flash"], "Nel 1518 centinaia di persone ballarono per giorni senza riuscire a fermarsi.",
             "In 1518, hundreds of people danced for days and couldn't stop."),
            ("b", None, [], "Strasburgo, luglio 1518.", "Strasbourg, July 1518."),
            ("c", None, [], "Una donna, Frau Troffea, scende in strada e inizia a ballare.",
             "A woman named Frau Troffea steps into the street and starts dancing."),
            ("c", Z1, [], "Non si ferma per giorni.", "She doesn't stop for days."),
            ("a", Z3, [], "Dopo una settimana, altre trenta persone ballano con lei.",
             "Within a week, thirty more people are dancing with her."),
            ("a", Z1, ["boom"], "Dopo un mese, secondo le cronache, sono centinaia.",
             "Within a month, chronicles say, there are hundreds."),
            ("f", None, [], "La soluzione delle autorità? Ancora più ballo.", "The authorities' solution? More dancing."),
            ("d", None, [], "Costruiscono un palco e pagano musicisti, convinti che ballando guariranno.",
             "They built a stage and hired musicians, convinced the dancers would dance it out."),
            ("e", None, ["scossa"], "Alcuni, secondo i racconti, crollano sfiniti.",
             "Some, according to accounts, collapse from exhaustion."),
            ("b", Z3, [], "Ancora oggi nessuno sa con certezza cosa sia successo.",
             "To this day, no one knows for sure what happened."),
            ("e", Z3, [], "L'ipotesi più accreditata: un'isteria di massa, dopo anni di fame e malattie.",
             "The leading theory: mass hysteria, after years of famine and disease."),
            ("a", Z2, [], *CTA),
        ]),
    "07-phineas-gage": dict(
        titolo=("SOPRAVVISSUTO", "PHINEAS GAGE"), titolo_en=("HE SURVIVED", "PHINEAS GAGE"),
        musica="Volatile-Reaction.mp3",
        evidenzia=["cranio", "esplosione", "sbarra"], evidenzia_en=["skull", "explosion", "rod"],
        immagini={
            "a": "portrait of a 19th century american railroad worker with a scar over one eye holding a long iron rod",
            "b": "1848 railroad construction site in Vermont hills, workers, rocks, tracks",
            "c": "19th century bearded male railroad worker pushing a long iron rod into a hole drilled in a rock, close-up",
            "d": "explosion of rock and dust at a railroad construction site, 1848",
            "e": "19th century wooden ox cart on a country road, injured man sitting up",
            "f": "old human skull and a long iron rod displayed in a museum glass case",
        },
        scene=[
            ("a", None, ["boom", "flash"], "Una sbarra di ferro gli attraversò il cranio. E lui si rialzò.",
             "An iron rod went straight through his skull. And he got up."),
            ("b", None, [], "Vermont, 1848. Phineas Gage lavora alla costruzione di una ferrovia.",
             "Vermont, 1848. Phineas Gage is building a railroad."),
            ("c", None, [], "Il suo compito: pressare la polvere da sparo nei fori con una sbarra di ferro.",
             "His job: pack blasting powder into holes with an iron rod."),
            ("d", None, ["boom", "flash", "scossa"], "Una scintilla. L'esplosione.", "A spark. An explosion."),
            ("a", Z1, [], "La sbarra, lunga più di un metro, entra sotto lo zigomo ed esce dalla cima della testa.",
             "The rod, over three feet long, enters under his cheekbone and exits through the top of his head."),
            ("d", Z3, [], "Atterra a venticinque metri di distanza.", "It lands about eighty feet away."),
            ("e", None, [], "Pochi minuti dopo, Phineas è seduto e parla.", "Minutes later, Phineas is sitting up and talking."),
            ("a", Z3, [], "Sopravvive. Ma chi lo conosceva dirà che non era più lo stesso.",
             "He survives. But people who knew him said he was no longer the same man."),
            ("b", Z3, [], "Il suo caso ha aiutato a capire come funziona il cervello.",
             "His case helped scientists understand how the brain works."),
            ("f", None, [], "Il suo cranio e la sbarra sono ancora conservati a Harvard.",
             "His skull and the rod are still kept at Harvard."),
            ("a", Z2, [], *CTA),
        ]),
    "08-stanislav-petrov": dict(
        titolo=("26 SETTEMBRE 1983", "IL MONDO A UN PASSO"), titolo_en=("SEPT 26, 1983", "THE WORLD ON THE EDGE"),
        musica="Hitman.mp3",
        evidenzia=["nucleare", "allarme", "cinque", "falso"], evidenzia_en=["nuclear", "alarm", "five", "false"],
        immagini={
            "a": "close-up portrait of a serious soviet officer in 1980s uniform, face lit by red glow, dark room, tension",
            "b": "snowy soviet military bunker entrance at night near Moscow, 1983, cold war",
            "c": "1980s soviet control room with large world map display and blinking red lights",
            "d": "red flashing warning light and big red button in a dark room, tension",
            "e": "satellite in orbit above clouds lit by the rising sun, earth from space",
            "f": "old soviet officer sitting alone in a simple apartment, quiet, melancholic",
        },
        scene=[
            ("a", None, ["boom", "flash"], "Quest'uomo ha probabilmente evitato una guerra nucleare. E quasi nessuno conosce il suo nome.",
             "This man probably prevented a nuclear war. And almost nobody knows his name."),
            ("b", None, [], "Vicino a Mosca, 26 settembre 1983. Piena Guerra Fredda.",
             "Near Moscow, September 26, 1983. The height of the Cold War."),
            ("c", None, [], "Stanislav Petrov è di turno nel bunker che sorveglia i missili americani.",
             "Stanislav Petrov is on duty in the bunker that watches for American missiles."),
            ("d", None, ["boom", "flash", "scossa"], "Dopo mezzanotte scatta l'allarme: un missile lanciato dagli Stati Uniti.",
             "After midnight, the alarm goes off: a missile launched from the United States."),
            ("c", Z1, [], "Poi due, tre… cinque missili.", "Then two, three… five missiles."),
            ("d", Z3, [], "Il protocollo è chiaro: avvisare subito i superiori. E potrebbe partire la risposta nucleare.",
             "Protocol is clear: report it immediately. And that could trigger nuclear retaliation."),
            ("a", Z1, [], "Petrov ragiona: un vero attacco userebbe centinaia di missili, non cinque.",
             "Petrov thinks: a real attack would use hundreds of missiles, not five."),
            ("a", Z3, [], "Decide che è un falso allarme. E non lo segnala come attacco.",
             "He decides it's a false alarm. And doesn't report it as an attack."),
            ("e", None, [], "Aveva ragione: il satellite aveva scambiato i riflessi del sole sulle nuvole per missili.",
             "He was right: the satellite had mistaken sunlight reflecting off clouds for missiles."),
            ("f", None, [], "Non ricevette nessuna medaglia. La storia rimase segreta per anni.",
             "He got no medal. The story stayed secret for years."),
            ("b", Z3, [], *CTA),
        ]),
    "09-ponte-di-tacoma": dict(
        titolo=("GALLOPING GERTIE", "IL PONTE CHE BALLAVA"), titolo_en=("GALLOPING GERTIE", "THE BRIDGE THAT DANCED"),
        musica="Volatile-Reaction.mp3",
        evidenzia=["vento", "crolla", "cane"], evidenzia_en=["wind", "collapses", "dog"],
        immagini={
            "a": "suspension bridge deck twisting and buckling like a ribbon over water in a storm, 1940, cables, dramatic",
            "b": "new 1940 suspension bridge over a wide strait, green hills, opening day, cars",
            "c": "1940s cars driving on a wavy undulating bridge deck, people amazed",
            "d": "suspension bridge deck breaking apart and falling into the water, concrete and steel debris",
            "e": "1940s car abandoned in the middle of a damaged bridge, wind",
            "f": "1940s engineers studying a bridge model in a wind tunnel laboratory",
        },
        scene=[
            ("a", None, ["boom", "flash"], "Questo ponte si è autodistrutto… per colpa del vento.",
             "This bridge destroyed itself… because of the wind."),
            ("b", None, [], "Stato di Washington, 1940. Inaugurano il ponte di Tacoma Narrows.",
             "Washington State, 1940. The Tacoma Narrows Bridge opens."),
            ("c", None, [], "Fin dal primo giorno, con un po' di vento, ondeggia su e giù.",
             "From day one, even a light wind makes it bounce up and down."),
            ("c", Z3, [], "Lo chiamano Galloping Gertie. C'è chi lo attraversa apposta per il brivido.",
             "People nickname it Galloping Gertie. Some drive across just for the thrill."),
            ("b", Z3, [], ("7 novembre 1940. Vento a sessanta chilometri all'ora.", "Sette novembre, millenovecentoquaranta. Vento a sessanta chilometri all'ora."),
             "November 7, 1940. Winds of forty miles per hour."),
            ("a", Z1, ["scossa"], "Il ponte inizia a torcersi come un nastro.", "The bridge starts twisting like a ribbon."),
            ("d", None, ["boom", "flash", "scossa"], "Verso le undici del mattino, crolla in acqua.",
             "Around eleven a.m., it collapses into the water."),
            ("e", None, [], "Nessuna vittima umana. L'unica fu un cane, rimasto in un'auto sul ponte.",
             "No people died. The only victim was a dog left in a car on the bridge."),
            ("f", None, [], "Quel crollo ha cambiato per sempre il modo di progettare i ponti.",
             "That collapse changed how bridges are designed forever."),
            ("a", Z3, [], *CTA),
        ]),
    "10-grande-puzza": dict(
        titolo=("LA GRANDE PUZZA", "LONDRA 1858"), titolo_en=("THE GREAT STINK", "LONDON 1858"),
        musica="Monkeys-Spinning-Monkeys.mp3",
        evidenzia=["puzzava", "fogna", "puzza"], evidenzia_en=["stank", "sewer", "smell"],
        immagini={
            "a": "victorian London gentlemen covering their noses with handkerchiefs by the dirty Thames river, 1858",
            "b": "victorian London skyline with Houses of Parliament under construction, hazy hot summer, 1858",
            "c": "dirty brown polluted river Thames with sewage pipes, victorian London, 1858",
            "d": "victorian parliament hall with curtains hanging over tall gothic windows, politicians in top hats",
            "e": "victorian engineer with large moustache looking at sewer construction plans",
            "f": "huge victorian brick sewer tunnel under construction, workers, arches",
        },
        scene=[
            ("a", None, ["boom", "flash"], "Nel 1858 Londra puzzava così tanto che il Parlamento quasi scappò.",
             "In 1858, London stank so badly that Parliament almost fled."),
            ("b", None, [], "Londra, estate 1858. Fa un caldo record.", "London, summer 1858. A heatwave hits."),
            ("c", None, [], "Il Tamigi è una fogna a cielo aperto: milioni di persone scaricano tutto nel fiume.",
             "The Thames is an open sewer for millions of people."),
            ("a", Z1, [], "Con il caldo, l'odore diventa insopportabile.", "In the heat, the smell becomes unbearable."),
            ("d", None, [], "In Parlamento appendono alle finestre tende imbevute di cloruro di calce.",
             "Parliament hangs curtains soaked in chloride of lime over the windows."),
            ("d", Z3, [], "Si pensa perfino di spostare il Parlamento fuori città.",
             "They even consider moving Parliament out of town."),
            ("b", Z3, ["flash"], "Poi, in meno di tre settimane, approvano una legge.",
             "Then, in under three weeks, they pass a law."),
            ("e", None, [], "L'ingegnere Joseph Bazalgette costruisce un'enorme rete di fogne.",
             "Engineer Joseph Bazalgette builds a massive sewer network."),
            ("f", None, [], "Quelle fogne funzionano ancora oggi.", "Those sewers are still in use today."),
            ("a", Z3, [], "Insomma: Londra è stata salvata da una puzza.", "So yes: London was saved by a bad smell."),
            ("c", Z3, [], *CTA),
        ]),
}


def frase(t):
    return {"testo": t[0], "voce": t[1]} if isinstance(t, tuple) else t


def main():
    for nome, s in STORIE.items():
        d = RADICE / nome
        d.mkdir(parents=True, exist_ok=True)
        slug = nome.split("-", 1)[1]
        out = {
            "output": f"{slug}.mp4", "output_en": f"{slug}-EN.mp4",
            "tempo_voce": 1.08,
            "titolo": {"testo": s["titolo"][0], "sotto": s["titolo"][1], "durata": 2.8},
            "titolo_en": {"testo": s["titolo_en"][0], "sotto": s["titolo_en"][1], "durata": 2.8},
            "evidenzia": s["evidenzia"], "evidenzia_en": s["evidenzia_en"],
            "musica": {"file": f"../../musica/{s['musica']}", "inizio": "auto", "volume": 0.4},
            "volume_effetti": 0.45,
            "scene": [],
        }
        for i, (img, rit, eff, it, en) in enumerate(s["scene"]):
            sc = {"immagine": img if "/" in img else f"immagini/{img}.png",
                  "frasi": [frase(it)], "frasi_en": [frase(en)]}
            if "/" not in img:
                sc["prompt"] = s["immagini"][img]
                sc["seme"] = sum(map(ord, nome + img))
            if rit:
                sc["ritaglio"] = rit
            if eff:
                sc["effetti"] = eff
            out["scene"].append(sc)
        (d / "scene.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print("scritto", d / "scene.json")


if __name__ == "__main__":
    main()
