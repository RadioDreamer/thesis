# Membránrendszer szimulációs szoftver kézikönyv

## A szoftverről

## Kezdő lépések

## Betöltés

Egy membránrendszer betöltéséhez két módot biztosít az alkalmazás:

1. Mentett membránrendszer betöltése ( *Menü* => *Fájl* => *Betöltés*)
    - Ilyenkor egy már meglévő fájlban lévő membránrendszer kerül betöltésre.
2. Membránrendszer konstruálása a struktúra és objektumok megadásával ( *Menü* => *Membránstruktúra megadása* )
    - Ilyenkor a felhasználónak kell a konstruálandó membránrendszer szöveges reprezentációját megadnia
    - A szoftver két membránrendszer típus szimulálására alkalmas, ezekhez pedig valamelyest eltérő szöveges
      reprezentációk tartoznak
    - Általánosan zárójelek jelzik a régiók kezdetét és végét, ezek között találhatók a bennük jelen lévő objektumok.
      Például egy alapmodell esetén "[aa[bb]]" a legkülső régió két darab 'a' objektumot tartalmaz, míg a benne lévő (
      gyerek) régió két darab 'b' objektumot
    - Közös követelmények mindkét esetben
        1. A megadott szövegben a zárójelezésnek validnak kell lennie (Minden nyitó zárójelnek van csukó párja, és
           nincsenek átfedések)
        2. Legalább egy zárójelpárt kell tartalmaznia a szövegnek

    - Alapmodell
        1. Alapmodell esetében ezen kívül feltétel, hogy a legkülső zárójelpáron kívül nem adhatunk meg objektumokat
    - Szimport-antiport rendszer
        1. Megadhatunk a legkülső zárójelpáron kívül is objektumokat, ezek fogják a környezet végtelenül rendelkezésre
           álló objektumait szolgálni (Ha ugyanazon objektum többször szerepel, akkor is *csak* végtelen
           multiplicitással lesz jelen a környezetben)
        2. Tartalmaznia kell az egyik zárójelpárnak egy '#' szimbólumot, ami azt jelzi, hogy a számítás eredményét annak
           a régiónak a tartalma fogja jelenteni (Ha több ilyet tartalmaz, akkor a feldolgozás során utoljára
           feldolgozott jelenti a végleges kimeneti régiót)
    - Meg kell jegyezni, hogy a struktúra és a benne lévő objektumok megadása nem elegendő ahhoz, hogy szimulálni
      tudjunk egy membránrendszert, hiszen evolúciós szabályok nélkül nincs változás a rendszerben

## Régiók szerkesztése

## Mentés

( *Menü* => *Mentés* )

- A szoftver lehetőséget biztosít felhasználó által megadott membránrendszer aktuális állapotának elmentésére. Ez nagyon
  hasznos tud lenni, hiszen ilyenkor nem kell minden alkalommal a struktúra megadásával majd szabályok hozzávételével
  újraalkotni egy kezdőállapotot, hanem elegendő csak betölteni.
- A mentés kezdeményezhető a menüsávból, de a **Ctrl+S** billentyűkombináció is hozzá van rendelve a funkcióhoz

## Szimuláció futtatása

- Miután megkonstruáltál egy membránrendszert, már csak egy dolog van hátra: szimulálni azt.
- A szimuláláshoz két funkciót biztosít a program:
    1. Lépésenkénti futtatás ( *Menü* => *Futtatás* => *Szimuláció lépés indítása*)
        - Ilyenkor a membránrendszerben csak egy evolúció zajlik vége, azaz minden régióban alkalmazzuk a kiválasztott
          szabályok multihalmazát
    2. Teljes szimuláció futtatása ( *Menü* => *Futtatás* => *Teljes szimuláció indítása*)
        - Ilyenkor a membránrendszer teljes számítása végbemegy, egy felugró ablakban pedig megjelenik a számítás
          eredménye