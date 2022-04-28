from PySide6.QtWidgets import (
    QDialog,
    QTextBrowser,
    QVBoxLayout,
    QTextEdit,
    QDialogButtonBox
)

from PySide6.QtGui import QTextCursor, QTextBlockFormat
from PySide6.QtCore import QFile, QIODevice, QDataStream

HELP_TEXT = ['# Membránrendszer szimulációs szoftver kézikönyv\n', '\n',
             '## A szoftverről\n', '\n', '## Kezdő lépések\n', '\n',
             '## Betöltés\n', '\n',
             'Egy membránrendszer betöltéséhez két módot biztosít az alkalmazás:\n',
             '\n',
             '1. Mentett membránrendszer betöltése ( *Menü* => *Fájl* => *Betöltés*)\n',
             '    - Ilyenkor egy már meglévő fájlban lévő membránrendszer kerül betöltésre.\n',
             '2. Membránrendszer konstruálása a struktúra és objektumok megadásával ( *Menü* => *Membránstruktúra megadása* )\n',
             '    - Ilyenkor a felhasználónak kell a konstruálandó membránrendszer szöveges reprezentációját megadnia\n',
             '    - A szoftver két membránrendszer típus szimulálására alkalmas, ezekhez pedig valamelyest eltérő szöveges\n',
             '      reprezentációk tartoznak\n',
             '    - Általánosan zárójelek jelzik a régiók kezdetét és végét, ezek között találhatók a bennük jelen lévő objektumok.\n',
             '      Például egy alapmodell esetén "[aa[bb]]" a legkülső régió két darab \'a\' objektumot tartalmaz, míg a benne lévő (\n',
             "      gyerek) régió két darab 'b' objektumot\n",
             '    - Közös követelmények mindkét esetben\n',
             '        1. A megadott szövegben a zárójelezésnek validnak kell lennie (Minden nyitó zárójelnek van csukó párja, és\n',
             '           nincsenek átfedések)\n',
             '        2. Legalább egy zárójelpárt kell tartalmaznia a szövegnek\n',
             '\n', '    - Alapmodell\n',
             '        1. Alapmodell esetében ezen kívül feltétel, hogy a legkülső zárójelpáron kívül nem adhatunk meg objektumokat\n',
             '    - Szimport-antiport rendszer\n',
             '        1. Megadhatunk a legkülső zárójelpáron kívül is objektumokat, ezek fogják a környezet végtelenül rendelkezésre\n',
             '           álló objektumait szolgálni (Ha ugyanazon objektum többször szerepel, akkor is *csak* végtelen\n',
             '           multiplicitással lesz jelen a környezetben)\n',
             "        2. Tartalmaznia kell az egyik zárójelpárnak egy '#' szimbólumot, ami azt jelzi, hogy a számítás eredményét annak\n",
             '           a régiónak a tartalma fogja jelenteni (Ha több ilyet tartalmaz, akkor a feldolgozás során utoljára\n',
             '           feldolgozott jelenti a végleges kimeneti régiót)\n',
             '    - Meg kell jegyezni, hogy a struktúra és a benne lévő objektumok megadása nem elegendő ahhoz, hogy szimulálni\n',
             '      tudjunk egy membránrendszert, hiszen evolúciós szabályok nélkül nincs változás a rendszerben\n',
             '\n', '## Régiók szerkesztése\n', '\n',
             '- Egy régió objektumainak és szabályainak szerkesztéséhez duplán kell kattintani a régió belsejébe\n',
             '- Ilyenkor egy felugró ablakban külön szövegdobozban adhatjuk meg a régió új objektumait a felső szövegdobozban\n',
             '  (alapértelmezett szövegként jelenik meg a régió jelenlegi objektumhalmaza), illetve új szabályait.\n',
             '- Az objektumok csak az angol ábécé kisbetűiből állhatnak ([a-z])\n',
             '\n', '### Szabályok helyes formátuma\n', '\n',
             '- Mivel a programmal két típusú membránrendszer szimulálható, ezért ezek külön feltételeket szabnak a szabályaik\n',
             '  alakjáról\n', '- Alapmodell\n', '    - Általánosan:\n',
             '      *1* ->(#) IN: *2* OUT: *3* HERE: *4*\n',
             '        1. A szabály úgynevezett bal oldala. Azokból az objektumokból áll, amelyeknek rendelkezésre kell állniuk a\n',
             '           régióban ahhoz, hogy végbemehessen az evolúciós lépés\n',
             '        2. A szabály alkalmazásának következtében a szülőbe vándorló objektumok\n',
             '        3. A szabály alkalmazásának következtében valamelyik gyerek régióba vándorló objektumok (nemdeterminisztikusan\n',
             '           választjuk ki, de csak akkor alkalmazható a szabály, ha legalább egy gyerekkel rendelkezik a régió)\n',
             '        4. A szabály alkalmazásának következtében keletkező helyben maradó objektumok\n',
             "    - Ha a bal és jobb oldalt elválasztó nyíl végén egy '#' szimbólum található, az azt jelenti, hogy az adott régió a\n",
             '      szabály alkalmazása után felbomlik\n',
             '    - Üres bal oldallal nem konstruálható szabály\n',
             '    - Az objektumok ebben az esetben is csak az angol ábécé kisbetűi lehetnek\n',
             '    - Ezen kívül megadható még prioritásos szabály, amelynek alakja:\n',
             '    *erősebb_szabály* > *gyengébb szabály*\n',
             '      - Mindaddig nem alkalmazhatjuk a gyengébb szabályt, ameddig az erősebb alkalmazható.\n',
             '- Szimport-antiport modell\n', '    - Általánosan:\n',
             '      IN: 1 OUT: 2 **VAGY** IN: 1 **VAGY** OUT: 2\n',
             '        1. A régióba beérkező objektumok\n',
             '        2. A régióból kivándorló objektumok\n',
             '    - Fontos megjegyezni, hogy ha a legelső típusú (antiport) szabályt szeretnénk megadni, olyankor mindkét irányba\n',
             '      kötelező, hogy legalább egy objektum mozogjon\n', '\n',
             '## Mentés\n', '\n', '( *Menü* => *Mentés* )\n', '\n',
             '- A szoftver lehetőséget biztosít felhasználó által megadott membránrendszer aktuális állapotának elmentésére. Ez nagyon\n',
             '  hasznos tud lenni, hiszen ilyenkor nem kell minden alkalommal a struktúra megadásával majd szabályok hozzávételével\n',
             '  újraalkotni egy kezdőállapotot, hanem elegendő csak betölteni.\n',
             '- A mentés kezdeményezhető a menüsávból, de a **Ctrl+S** billentyűkombináció is hozzá van rendelve a funkcióhoz\n',
             '\n', '## Szimuláció futtatása\n', '\n',
             '- Miután megkonstruáltál egy membránrendszert, már csak egy dolog van hátra: szimulálni azt.\n',
             '- A szimuláláshoz két funkciót biztosít a program:\n',
             '    1. Lépésenkénti futtatás ( *Menü* => *Futtatás* => *Szimuláció lépés indítása*)\n',
             '        - Ilyenkor a membránrendszerben csak egy evolúció zajlik vége, azaz minden régióban alkalmazzuk a kiválasztott\n',
             '          szabályok multihalmazát\n',
             '    2. Teljes szimuláció futtatása ( *Menü* => *Futtatás* => *Teljes szimuláció indítása*)\n',
             '        - Ilyenkor a membránrendszer teljes számítása végbemegy, egy felugró ablakban pedig megjelenik a számítás\n',
             '          eredménye']


class HelpMenu(QDialog):
    """
    A class for displaying helpful information to the user using the simulator

    Attributes
    ----------
    button_box : QDialogButtonBox
        the button box to accept user input
    help_md : QTextEdit
        the text field for displaying the guide
    """

    def __init__(self, parent=None):
        """
        A function for initializing the guide

        Parameters
        ----------
        parent : QObject
            the parent of the dialog window
        """

        super().__init__(parent)
        self.setMinimumSize(750, 400)
        self.setWindowTitle("Használati útmutató")

        QBtn = QDialogButtonBox.StandardButton.Ok
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.setCenterButtons(True)

        # Original Markdown Layout
        self.help_md = QTextEdit(self)
        self.help_md.setReadOnly(True)
        self.help_md.resize(800, 800)
        self.help_md.setMarkdown('\n'.join(HELP_TEXT))

        # Scale the space between the lines
        block_fmt = QTextBlockFormat()
        block_fmt.setLineHeight(150, QTextBlockFormat.ProportionalHeight)
        cursor = self.help_md.textCursor()
        cursor.clearSelection()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_fmt)

        # Put the two widgets into a layout
        layout = QVBoxLayout()
        layout.addWidget(self.help_md)
        layout.addWidget(self.button_box)
        self.setLayout(layout)
