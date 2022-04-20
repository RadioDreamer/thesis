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
from PySide6.QtCore import QRectF, QObject, Signal


class ModelType(Enum):
    """
    An enum class responsible for describing the type of the membrane system

    Currently there are two types supported
    """

    BASE = 0
    SYMPORT = 1


class SimulatorSignal(QObject):
    """
    A class to represent the signals which can be emitted by the simulator

    Attributes
    ----------
    simulation_over : Signal
        the signal that communicates to the view that the simulation has ended
    counter_increment : Signal
        the signal that communicates to the view that the number of simulation
        steps has increased
    """

    simulation_over = Signal(dict)
    counter_increment = Signal(int)


class MembraneSimulator(QWidget):
    """
    A class responsible for communicating with the model of the membrane system
    and displaying its current state for the view

    Attributes
    ----------
    type : ModelType
        the type of the model being simulated
    skin_id : int
        the identifier of the skin (root node in the structure) in the model
    model : MembraneSystem
        the model of the membrane system (business logic)
    scene : QGraphicsScene
        the widget which holds the view of the regions in the simulator
    view :  QGraphicsView
        the widget which is responsible for displaying the `scene`
    view_regions : dict
        the dictionary with the keys being the region identifiers and values
        are the corresponding `RegionView` objects (the displayed regions)
    signal : SimulatorSignalSignal
        the objects for containing all the available signals to be emitted
    max_width : int
        the maximum width for the rectangle of the skin region
    max_height : int
        the maximum height for the rectangle of the skin region
    """

    def __init__(self, max_width, max_height, parent=None):
        """
        A function to initialize the simulator

        Parameters
        ----------
        max_width : int
            the maximum width for the rectangle of the skin region
        max_height : int
            the maximum height for the rectangle of the skin region
        parent : QWidget
            the parent widget of the simulator
        """

        super().__init__(parent)
        self.type = None
        self.skin_id = None
        self.model = None
        self.scene = QGraphicsScene()
        self.view = QGraphicsView()
        self.view_regions = {}
        self.view.setScene(self.scene)
        self.signal = SimulatorSignal()
        self.max_width = max_width
        self.max_height = max_height

    def set_model_object(self, model_obj):
        """
        A function used to set the model to `moodel_obj` in the simulator

        This function is called whenever the user loads a pre-configured
        membrane system from a file

        Parameters
        ----------
        model_obj : MembraneSystem
            the membrane system loaded from a file
        """

        if isinstance(model_obj, BaseModel):
            self.type = ModelType.BASE
        elif isinstance(model_obj, SymportAntiport):
            self.type = ModelType.SYMPORT

        self.model = model_obj
        self.model.signal.sim_over.connect(self.signal.simulation_over.emit)
        self.model.signal.sim_step_over.connect(
            self.signal.counter_increment.emit)
        self.model.signal.obj_changed.connect(self.update_obj_view)
        self.model.signal.rules_changed.connect(self.update_rule_view)
        self.model.signal.region_dissolved.connect(self.update_dissolve)
        self.draw_model()

    def set_model(self, type, string):
        """
        A function used to construct to model of the membrane system from the
        given string and the type

        Depending on `type`, one of MembraneSystem subclass's
        `create_model_from_str` will be called

        After constructing the model `draw_model()` is called, visualizing the
        current state of the model

        Parameters
        ----------
        type : ModelType
            the type of model to be created
        string : str
            the string containing information on how to construct the membrane
            system
        """

        if type == ModelType.BASE:
            self.model = BaseModel.create_model_from_str(string)
            self.type = ModelType.BASE
        elif type == ModelType.SYMPORT:
            self.type = ModelType.SYMPORT
            self.model = SymportAntiport.create_model_from_str(string)

        self.model.signal.sim_over.connect(self.signal.simulation_over.emit)
        self.model.signal.sim_step_over.connect(
            self.signal.counter_increment.emit)
        self.model.signal.obj_changed.connect(self.update_obj_view)
        self.model.signal.rules_changed.connect(self.update_rule_view)
        self.model.signal.region_dissolved.connect(self.update_dissolve)
        self.draw_model()

    def update_dissolve(self, id):
        """
        A function to update the scene of the membrane system on the event of a
        region dissolving

        Parameters
        ----------
        id : int
            the identifier of the region that is dissolving
        """

        self.scene.removeItem(self.view_regions[id])
        del self.view_regions[id]

    def update_obj_view(self, id, string):
        """
        A function to update the scene of the membrane system when a region's
        objects change

        Parameters
        ----------
        id : int
            the identifier of the region whose objects changed
        string : str
            the string containing the new objects string representation
        """

        self.view_regions[id].obj_text.setText(string)

    def update_rule_view(self, id, string):
        """
        A function to update the scene of the membrane system when a region's
        rules change

        Parameters
        ----------
        id : int
            the identifier of the region whose objects changed
        string : str
            the string containing the new list of rules in a string format
        """

        self.view_regions[id].rule_text.setText(string)

    def draw_model(self):
        """
        A function that is responsible for visualizing the membrane system
        """

        self.scene.clear()
        self.skin_id = self.model.get_root_id()
        self.view_regions[self.skin_id] = RegionView(self.skin_id,
                                                     QRectF(0, 0,
                                                            self.max_width,
                                                            self.max_height),
                                                     str(
                                                         self.model.regions[
                                                             self.skin_id].objects),

                                                     self.model.regions[
                                                         self.skin_id].get_rule_string(),
                                                     simulator=self)
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
                                                             self.model.regions[
                                                                 child.id].get_rule_string(),
                                                             simulator=self,
                                                             parent=
                                                             self.view_regions[
                                                                 current_node_id])
                    self.view_regions[child.id].setPos(i * child_width, 0)
                gen_child_list.remove(current_node_id)
        self.view.show()

    @classmethod
    def is_valid_structure(cls, string):
        """
        A class method for deciding if the given string contains a valid structure
        for a membrane system

        This function only calls the model's own ˙is_valid_parentheses()`

        Parameters
        ----------
        string : str
            the string containing the structure to be checked

        Returns
        -------
        bool
            True if it is a valid string, False otherwise
        """

        return MembraneSystem.is_valid_parentheses(string)

    # def show_membranes(self):
    #     self.view_regions[self.skin_id].show()
    #
    # def hide_membranes(self):
    #     self.view_regions[self.skin_id].hide()

    # def is_visible(self):
    #     return self.view_regions[self.skin_id].isVisible()

    def update_region_objects(self, id, new_objects: str):
        """
        A function that takes the user input and sets the region's object to the
        new multiset generated

        Parameters
        ----------
        id : int
            the identifier of region whose objects are changed
        new_objects : str
            the user input which will be parsed
        """

        new_multiset = MultiSet.string_to_multiset(new_objects)
        self.model.regions[id].objects = new_multiset

    def update_region_rules(self, id, new_rules: str):
        """
        A function that sets the region's rules to ones
        generated by parsing the user's input

        Parameters
        ----------
        id : int
            the identifier of region whose rules are changed
        new_rules : str
            the user input which will be parsed
        """

        new_rule_list = self.model.__class__.string_to_rules(new_rules)
        self.model.regions[id].rules = new_rule_list

    def simulate_step(self):
        """
        A function to simulate a step in the membrane system

        Essentially calls the model's `simulate_step()` function
        """

        self.model.simulate_step()

    def simulate_computation(self):
        """
        A function to simulate the whole computation the membrane system

        Essentially a wrapper around the model's `simulate_computation()`
        function
        """

        self.model.simulate_computation()

    def save_model(self, name):
        """
        A function to save the simulator's model to a file with the given path

        Essentially a wrapper around the model's `save()`
        function

        Parameters
        ----------
        name : str
            the absolute path to the file
        """

        self.model.save(name)

    def load_model(self, name):
        """
        A function to load the model from a file

        Parameters
        ----------
        name : str
            the absolute path to the file
        """

        with open(name, 'r') as load_file:
            json_dict = json.load(load_file)
        if json_dict["type"] == 'BaseModel':
            model = BaseModel.load(json_dict)
        elif json_dict["type"] == 'SymportAntiport':
            model = SymportAntiport.load(json_dict)
        self.set_model_object(model)
