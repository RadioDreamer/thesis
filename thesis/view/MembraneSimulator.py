from enum import Enum
from PySide6.QtWidgets import (
    QWidget,
    QGraphicsScene,
    QGraphicsView,
    QMessageBox
)

from MembraneSystem import MembraneSystem
from BaseModel import BaseModel
from SymportAntiport import SymportAntiport
from MultiSet import MultiSet
from RegionView import RegionView
from PySide6.QtCore import QRectF


class ModelType(Enum):
    BASE = 0
    SYMPORT = 1


class MembraneSimulator(QWidget):
    def __init__(self, max_width, max_height, parent=None):
        super().__init__(parent)
        self.type = None
        self.skin_id = None
        self.model = None
        self.scene = QGraphicsScene()
        self.view = QGraphicsView()
        self.regions = {}
        self.view.setScene(self.scene)

        self.max_width = max_width
        self.max_height = max_height

    #    @classmethod
    #    def is_valid_rule(cls, rule_str):
    #        return MembraneSystem.is_valid_rule(rule_str)

    def simulation_over(self):
        msg_box = QMessageBox()
        msg_box.setText("Simulation Over!")
        msg_box.exec()

    def set_model(self, type, string):
        if type == ModelType.BASE:
            self.model = BaseModel.create_model_from_str(string)
            self.type = ModelType.BASE
        elif type == ModelType.SYMPORT:
            self.type = ModelType.SYMPORT
            self.model = SymportAntiport.create_model_from_str(string)
        self.model.signal.sim_over.connect(self.simulation_over)
        self.model.signal.obj_changed.connect(self.update_obj_view)
        self.model.signal.rules_changed.connect(self.update_rule_view)
        self.draw_model()

    def update_obj_view(self, id, string):
        self.regions[id].obj_text.setText(string)

    def update_rule_view(self, id, string):
        print("UPDATE", string)
        self.regions[id].rule_text.setText(string)

    def draw_model(self):
        self.scene.clear()
        self.skin_id = self.model.get_root_id()
        self.regions[self.skin_id] = RegionView(self.skin_id,
                                                QRectF(0, 0, self.max_width,
                                                       self.max_height), str(
                self.model.regions[self.skin_id].objects), "", simulator=self)
        self.scene.addItem(self.regions[self.skin_id])

        children = self.model.get_child(self.model.regions[self.skin_id])
        self.regions[children.id] = RegionView(children.id,
                                               QRectF(0, 0, self.max_width / 2,
                                                      self.max_height / 2), str(
               self.model.regions[children.id].objects), "", simulator=self, parent=self.regions[self.skin_id])
        self.view.show()

    @classmethod
    def is_valid_structure(cls, string):
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
        self.model.regions[id].rules = new_rule_list

    def simulate_step(self):
        self.model.simulate_step()

    def simulate_computation(self):
        print(self.model)
        self.model.simulate_computation()
