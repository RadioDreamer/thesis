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

- Egy régió objektumainak és szabályainak szerkesztéséhez duplán kell kattintani a régió belsejébe
- Ilyenkor egy felugró ablakban külön szövegdobozban adhatjuk meg a régió új objektumait a felső szövegdobozban
  (alapértelmezett szövegként jelenik meg a régió jelenlegi objektumhalmaza), illetve új szabályait.
- Az objektumok csak az angol ábécé kisbetűiből állhatnak ([a-z])

### Szabályok helyes formátuma

- Mivel a programmal két típusú membránrendszer szimulálható, ezért ezek külön feltételeket szabnak a szabályaik
  alakjáról
- Alapmodell
    - Általánosan:
      *1* ->(#) IN: *2* OUT: *3* HERE: *4*
        1. A szabály úgynevezett bal oldala. Azokból az objektumokból áll, amelyeknek rendelkezésre kell állniuk a
           régióban ahhoz, hogy végbemehessen az evolúciós lépés
        2. A szabály alkalmazásának következtében a szülőbe vándorló objektumok
        3. A szabály alkalmazásának következtében valamelyik gyerek régióba vándorló objektumok (nemdeterminisztikusan
           választjuk ki, de csak akkor alkalmazható a szabály, ha legalább egy gyerekkel rendelkezik a régió)
        4. A szabály alkalmazásának következtében keletkező helyben maradó objektumok
    - Ha a bal és jobb oldalt elválasztó nyíl végén egy '#' szimbólum található, az azt jelenti, hogy az adott régió a
      szabály alkalmazása után felbomlik
    - Üres bal oldallal nem konstruálható szabály
    - Az objektumok ebben az esetben is csak az angol ábécé kisbetűi lehetnek
    - Ezen kívül megadható még prioritásos szabály, amelynek alakja:
    *erősebb_szabály* > *gyengébb szabály*
      - Mindaddig nem alkalmazhatjuk a gyengébb szabályt, ameddig az erősebb alkalmazható.
- Szimport-antiport modell
    - Általánosan:
      IN: 1 OUT: 2 **VAGY** IN: 1 **VAGY** OUT: 2
        1. A régióba beérkező objektumok
        2. A régióból kivándorló objektumok
    - Fontos megjegyezni, hogy ha a legelső típusú (antiport) szabályt szeretnénk megadni, olyankor mindkét irányba
      kötelező, hogy legalább egy objektum mozogjon

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