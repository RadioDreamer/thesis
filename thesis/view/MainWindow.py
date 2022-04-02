import sys
from enum import Enum

sys.path.append("../model")
from PySide6.QtWidgets import (
QMainWindow, QApplication, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsProxyWidget, QLabel,
QWidget, QGraphicsItem, QGraphicsWidget, QGraphicsRectItem, QGraphicsSimpleTextItem, QPushButton, QVBoxLayout, QStatusBar, QDialog,
QLineEdit, QDialogButtonBox, QPlainTextEdit, QMessageBox
)

from PySide6.QtGui import QPen, QBrush, QColor, QResizeEvent, QPainter, QAction
from PySide6.QtCore import QRectF
from MembraneSystem import MembraneSystem
from BaseModel import BaseModel
from SymportAntiport import SymportAntiport
from MultiSet import MultiSet

SKIN_X = 800
SKIN_Y = 800


class ModelType(Enum):
    BASE = 0
    SYMPORT = 1


class MembraneRuleAndObjectEditDialog(QDialog):
    def __init__(self, region_objects, valid_fn=None,type=None, rules=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Régió szerkesztése")
        self.valid_fn = valid_fn
        self.rules = rules
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        obj_msg = QLabel("Add meg a régió új objektumait!")
        self.object_edit = QLineEdit()
        # self.object_edit.setPlaceholderText(region_objects)
        self.object_edit.setText(region_objects)

        rule_msg = QLabel("A régió jelenlegi szabályai!")
        self.rule_edit_list = QPlainTextEdit(self.rules)
        self.layout.addWidget(obj_msg)
        self.layout.addWidget(self.object_edit)
        self.layout.addWidget(rule_msg)
        self.layout.addWidget(self.rule_edit_list)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def get_rules(self):
        return self.rules

    def accept(self):
        if self.rules == self.rule_edit_list.toPlainText():
            super().accept()

        rule_list = self.rule_edit_list.toPlainText().split('\n')
        cond = True
        for rule in rule_list:
            if not self.valid_fn(rule):
                cond = False
                break

        if not cond:
            msg_box = QMessageBox()
            msg_box.setText("Nem megfelelő!")
            msg_box.exec()
        else:
            super().accept()


class MembraneStructureDialog(QDialog):
    def __init__(self, parent=None, valid_fn=None):
        super().__init__(parent)
        self.setWindowTitle("Membránstruktúra megadása")
        self.valid_fn = valid_fn
        self.text = ""
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(QBtn)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        msg = QLabel("Add meg a membránstruktúra szöveges reprezentációját!")
        edit = QLineEdit()

        edit.textChanged.connect(self.set_text)
        self.layout.addWidget(msg)
        self.layout.addWidget(edit)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def accept(self):
        if self.valid_fn(self.text):
            super().accept()
        else:
            msg_box = QMessageBox()
            msg_box.setText("Not a valid membrane system!")
            msg_box.exec()

    def set_text(self, string):
        self.text = string

    def get_text(self):
        return self.text

class MyText(QGraphicsRectItem):
    def __init__(self, id, rect, obj, rules, simulator=None, parent=None):
        super().__init__(rect, parent)
        self.id = id
        self.simulator = simulator
        self.obj_text = QGraphicsSimpleTextItem(obj, self)
        self.rule_text = QGraphicsSimpleTextItem(rules, self)
        text_rect = QRectF(self.obj_text.boundingRect())
        rule_rect = QRectF(self.rule_text.boundingRect())
        self.obj_text.setPos((rect.width() - text_rect.width())/2, 0)
        self.rule_text.setPos((rect.width() - rule_rect.width())/2, text_rect.height())

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setPen(QPen(QBrush(QColor('blue')), 3))

    def mouseDoubleClickEvent(self, event):
        # Itt lehet majd editelni az objektumokat és a szabályokat
        objects = self.simulator.model.regions[self.id].objects
        rule_string = self.simulator.model.get_rule_string(self.id)

        valid_fn = self.simulator.model.__class__.is_valid_rule
        dialog = MembraneRuleAndObjectEditDialog(str(objects), valid_fn=valid_fn, rules=rule_string, type=self.simulator.type)
        dialog.exec()

        rule_result = dialog.get_rules()
        if not rule_result == rule_string:
            self.simulator.update_region_rules(self.id, rule_result)

        obj_result = MyText.sort_word(dialog.object_edit.text())
        if obj_result != MyText.sort_word(self.obj_text.text()):
            self.simulator.update_region_objects(self.id, obj_result)

    @classmethod
    def sort_word(cls, string):
        return ''.join(sorted(string, key=str.lower))


class MembraneSimulator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.type = None
        self.skin_id = None
        self.model = None
        self.scene = QGraphicsScene()
        self.view = QGraphicsView()
        self.regions = {}
        self.view.setScene(self.scene)
        # self.view.show()

    @classmethod
    def is_valid_rule(cls, rule_str):
        return MembraneSystem.is_valid_rule(rule_str)

    def simulation_over(self):
        msg_box = QMessageBox()
        msg_box.setText("Simulation Over!")
        msg_box.exec()

    def set_model(self, type, string):
        if type == ModelType.BASE:
            self.model = BaseModel.create_from_str(string)
            self.type = ModelType.BASE
        elif type == ModelType.SYMPORT:
            self.type = ModelType.SYMPORT
            self.model = SymportAntiport.create_from_str(string)
        self.model.signal.sim_over.connect(self.simulation_over)
        self.model.signal.obj_changed.connect(self.update_obj_view)
        self.model.signal.rules_changed.connect(self.update_rule_view)
        self.draw_model()

    def update_obj_view(self, id, string):
        self.regions[id].obj_text.setText(string)

    def update_rule_view(self, id, string):
        self.regions[id].rule_text.setText(string)

    def draw_model(self):
        self.scene.clear()
        self.skin_id = self.model.get_root_id()
        self.regions[self.skin_id] = MyText(self.skin_id, QRectF(0, 0, SKIN_X, SKIN_Y), str(self.model.regions[self.skin_id].objects),'a->c', simulator=self)
        self.scene.addItem(self.regions[self.skin_id])
        self.view.show()

    @classmethod
    def is_valid_string(cls, string):
        return MembraneSystem.is_valid_parentheses(string)

    def show_membranes(self):
        self.regions[self.skin_id].show()

    def hide_membranes(self):
        self.regions[self.skin_id].hide()

    def is_visible(self):
        return self.regions[self.skin_id].isVisible()

    def update_region_objects(self, id, new_objects: str):
        new_multiset = MultiSet.string_to_multiset(new_objects)
        self.model.regions[id].objects = new_multiset

    def update_region_rules(self, id, new_rules: str):
        new_rule_list = self.model.__class__.string_to_rules(new_rules)
        self.model.regions[id].objects = new_rule_list

    def simulate_step(self):
        self.model.simulate_step()
        self.update()
        if self.model.is_over():
            pass

    def simulate_computation(self):
        print(self.model.regions)
        self.model.simulate_computation()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Membránrendszer szimuláció")
        container = QWidget()
        self.setCentralWidget(container)
        self.membranes = MembraneSimulator()

        menu = self.menuBar()

        save_action = QAction("Mentés", self)
        load_action = QAction("Betöltés", self)

        # Fájl menü
        file_menu = menu.addMenu("Fájl")
        file_menu.addActions([save_action, load_action])

        # Struktúra megadásához menü
        create_menu = menu.addMenu("Membránstruktúra megadása")
        create_base_action = QAction("Alapmodell megadása", self)
        create_symport_action = QAction("Szimport/Antiport modell megadása", self)
        create_menu.addActions([create_base_action, create_symport_action])

        create_base_action.triggered.connect(self.create_base_dialog)

        # Futtatáshoz tartozó menü
        run_menu = menu.addMenu("Futtatás")
        run_step = QAction("Szimuláció lépés futtatása", self)
        run_sim = QAction("Teljes szimuláció indítása", self)
        run_menu.addActions([run_sim, run_step])
        run_step.triggered.connect(self.membranes.simulate_step)
        run_sim.triggered.connect(self.membranes.simulate_computation)

        self.setStatusBar(QStatusBar(self))
        self.statusBar().addPermanentWidget(QPushButton("Teljes szimuláció indítása"))
        self.statusBar().addPermanentWidget(QPushButton("Szimuláció lépés indítása"))
        self.statusBar().addPermanentWidget(QLabel("Lépések száma: 0"))
        self.statusBar().hide()

        self.button = QPushButton("Press me")
        self.button.pressed.connect(self.btn_pressed)
        layout = QVBoxLayout()
        layout.addWidget(self.button)

#        region = MyText(0, QRectF(0, 0, 100, 100), "Hello World")
#        child_region = MyText(1, QRectF(0, 0, 50, 50), "Child", region)
#        child_region2 = MyText(2, QRectF(0, 0, 30, 30), "Child2", region)

#        self.membranes.regions[0] = region
#        self.membranes.regions[1] = child_region
#        self.membranes.regions[2] = child_region2

        layout.addWidget(self.membranes.view)
        # self.membranes.show_scene()
        container.setLayout(layout)

    def btn_pressed(self):
        if self.membranes.is_visible():
            self.membranes.hide_membranes()
        else:
            self.membranes.show_membranes()

    def create_base_dialog(self):
        dialog = MembraneStructureDialog(self, MembraneSimulator.is_valid_string)
        dialog.exec()
        self.membranes.set_model(ModelType.BASE, dialog.get_text())
        self.statusBar().show()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


# import sys
# import random
#
# from PySide6.QtWidgets import (
# QMainWindow, QApplication, QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsProxyWidget, QLabel,
# QWidget, QGraphicsItem, QGraphicsWidget, QGraphicsRectItem, QGraphicsSimpleTextItem, QPushButton, QVBoxLayout
# )
# from PySide6.QtGui import QPen, QBrush, QColor, QResizeEvent, QPainter
# from PySide6.QtCore import QRectF
#
# class MyText(QGraphicsRectItem):
#     def __init__(self, rect, text, parent=None):
#         super().__init__(rect, parent)
#         self.text = QGraphicsSimpleTextItem(text, self)
#         text_rect = QRectF(self.text.boundingRect())
#         self.text.setPos((rect.width() - text_rect.width())/2, 0)
#         self.setFlag(QGraphicsItem.ItemIsMovable, True)
#         # self.setPen(QPen(QBrush(QColor('blue')), 5))
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Experiment")
#
#         self.button = QPushButton("Press me")
#         self.button.pressed.connect(self.btn_pressed)
#         layout = QVBoxLayout()
#         layout.addWidget(self.button)
#         self.regions = {}
#         container = QWidget()
#
#         self.setCentralWidget(container)
#
#         scene = QGraphicsScene(0, 0, 800, 800)
#
#         region = MyText(QRectF(0, 0, 100, 100), "Hello World")
#         child_region = MyText(QRectF(0, 0, 50, 50), "Child", region)
#         child_region2 = MyText(QRectF(0, 0, 30, 30), "Child2", region)
#
#         self.regions[0] = region
#         self.regions[1] = child_region
#         self.regions[2] = child_region2
#         scene.addItem(region)
#
#         view = QGraphicsView()
#         layout.addWidget(view)
#         view.setScene(scene)
#         view.show()
#         container.setLayout(layout)
#
#     def btn_pressed(self):
#         self.regions[1].text.setText(f"{random.randint(0,10)}")
#
# if __name__ == "__main__":
#     app = QApplication([])
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec())

