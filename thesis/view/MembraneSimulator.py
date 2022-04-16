import json
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
        self.view_regions = {}
        self.view.setScene(self.scene)

        self.max_width = max_width
        self.max_height = max_height

    #    @classmethod
    #    def is_valid_rule(cls, rule_str):
    #        return MembraneSystem.is_valid_rule(rule_str)

    def simulation_over(self, result):
        print("ENV", self.model.environment.objects)
        print("RESULT", result)
        msg_box = QMessageBox()
        msg_box.setText(f"Simulation Over!\nResult:{result}")
        msg_box.exec()

    def set_model_object(self, model_obj):
        if isinstance(model_obj, BaseModel):
            self.type = ModelType.BASE
        elif isinstance(model_obj, SymportAntiport):
            self.type = ModelType.SYMPORT
        self.model = model_obj
        self.model.signal.sim_over.connect(self.simulation_over)
        self.model.signal.obj_changed.connect(self.update_obj_view)
        self.model.signal.rules_changed.connect(self.update_rule_view)
        self.model.signal.region_dissolved.connect(self.update_dissolve)
        self.draw_model()

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
        self.model.signal.region_dissolved.connect(self.update_dissolve)
        self.draw_model()

    def update_dissolve(self, id):
        self.scene.removeItem(self.view_regions[id])
        del self.view_regions[id]

    def update_obj_view(self, id, string):
        self.view_regions[id].obj_text.setText(string)

    def update_rule_view(self, id, string):
        self.view_regions[id].rule_text.setText(string)

    def draw_model(self):
        self.scene.clear()
        self.skin_id = self.model.get_root_id()
        self.view_regions[self.skin_id] = RegionView(self.skin_id,
                                                     QRectF(0, 0,
                                                            self.max_width,
                                                            self.max_height),
                                                     str(
                                                         self.model.regions[
                                                             self.skin_id].objects),
                                                     "", simulator=self)
        self.scene.addItem(self.view_regions[self.skin_id])

        gen_child_list = [self.skin_id]
        while gen_child_list:
            current_node_id = gen_child_list[0]
            if self.model.get_num_of_children(
                    self.model.regions[current_node_id]) == 0:
                gen_child_list.remove(current_node_id)
            else:
                children = self.model.get_all_children(
                    self.model.regions[current_node_id])
                child_width = self.view_regions[
                                  current_node_id].rect().width() / (2 * len(
                    children))
                child_height = self.view_regions[
                                   current_node_id].rect().height() / (2 * len(
                    children))

                for i, child in enumerate(children):
                    gen_child_list.append(child.id)
                    self.view_regions[child.id] = RegionView(child.id,
                                                             QRectF(0, 0,
                                                                    child_width,
                                                                    child_height),
                                                             str(
                                                                 self.model.regions[
                                                                     child.id].objects),
                                                             "",
                                                             simulator=self,
                                                             parent=
                                                             self.view_regions[
                                                                 current_node_id])
                    self.view_regions[child.id].setPos(i * child_width, 0)
                gen_child_list.remove(current_node_id)
        self.view.show()

    @classmethod
    def is_valid_structure(cls, string):
        return MembraneSystem.is_valid_parentheses(string)

    def show_membranes(self):
        self.view_regions[self.skin_id].show()

    def hide_membranes(self):
        self.view_regions[self.skin_id].hide()

    def is_visible(self):
        return self.view_regions[self.skin_id].isVisible()

    def update_region_objects(self, id, new_objects: str):
        new_multiset = MultiSet.string_to_multiset(new_objects)
        self.model.regions[id].objects = new_multiset

    def update_region_rules(self, id, new_rules: str):
        new_rule_list = self.model.__class__.string_to_rules(new_rules)
        self.model.regions[id].rules = new_rule_list

    def simulate_step(self):
        self.model.simulate_step()

    def simulate_computation(self):
        self.model.simulate_computation()

    def save_model(self, name):
        self.model.save(name)

    def load_model(self, name):
        with open(name, 'r') as load_file:
            json_dict = json.load(load_file)
        if json_dict["type"] == 'BaseModel':
            model = BaseModel.load(json_dict)
        elif json_dict["type"] == 'SymportAntiport':
            model = SymportAntiport.load(json_dict)
        self.set_model_object(model)
