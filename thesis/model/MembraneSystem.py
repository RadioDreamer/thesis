import random
import json
from typing import Dict, List
from MultiSet import MultiSet
from MultiSet import InvalidOperationException
from PySide6.QtCore import QObject, Signal


class InvalidArgumentException(Exception):
    """
    A class to signal an exception regarding incorrect arguments given to a
    function
    """
    pass


class Environment(MultiSet):
    """
    A class for representing the environment of the membrane system

    It can have special objects, which are of infinite multiplicity, thus always
    available for evolution

    Attributes
    ----------
    infite_obj : list
        the list containing the objects with infinite multiplicity
    objects : dict
        a dict containing the objects as keys and their multiplicity as values
    """

    def __init__(self, objects=None, infinite_obj=None):
        """
        A function used for initializing the environment

        Parameters
        ----------

        objects : dict, optional
            the dictionary containing the objects for the initial state of the
            environment (default is None)
        infinite_obj : list, optional
            the list containing the objects with infinite
            multiplicity (default is None)
        """

        super().__init__(objects)
        self.infinite_obj = set(infinite_obj) if infinite_obj else None
        if infinite_obj is not None:
            delete = [obj for obj in self.objects if obj in infinite_obj]
            for obj in delete:
                del self[obj]

    def has_subset(self, multiset):
        """
        A function used to determine whether a multiset is a subset of the
        environment

        The method of checking this condition is almost the same as with the
        base class `MultiSet`, but here we need to take into consideration that
        the environment can have objects with infinite multiplicity

        Parameters
        ----------
        multiset : MultiSet
            the multiset we want to check whether if it is a multiset

        Returns
        -------
        bool
            True if it is a multiset, False otherwise
        """

        for obj, mul in multiset:
            if obj in self and self[obj] >= mul:
                pass
            elif self.infinite_obj and obj in self.infinite_obj:
                pass
            else:
                return False
        return True

    def __add__(self, multiset):
        """
        A function used to add a multiset to the environment

        This function is invalid for `Environment` instances, so it is
        purposefully left unimplemented

        Parameters
        ----------
        multiset : MultiSet
            the multiset we add to `self`

        Raises
        -------
        InvalidOperationException
            every time one calls the function
        """

        raise InvalidOperationException

    def __sub__(self, multiset):
        """
        A function used to subtract a multiset from the environment

        This function is invalid for `Environment` instances, so it is
        purposefully left unimplemented

        Parameters
        ----------
        multiset : MultiSet
         -------
        InvalidOperationException
            every time one calls the function
        """

        raise InvalidOperationException

    def __iadd__(self, multiset):
        """
        A function used to add a multiset to the environment

        Adding as an operation with a multiset means that the shared
        objects' multiplicity adds up and the ones that are only present in
        of the multisets are simply added to the resulting multiset with
        their starting multiplicity. If the multiset has an object of which the
        environment has infinite multiplicity of it simply stays that way.

        Parameters
        ----------
        multiset : MultiSet
            the multiset we want to add to `self`

        Returns
        -------
        Environment
            the `self` object we added `multiset` to
        """

        for obj, mul in multiset:
            if obj in self.infinite_obj:
                pass
            elif obj in self.objects:
                self[obj] += mul
            else:
                self[obj] = mul

        return self

    def __isub__(self, multiset):
        """
        A function used to subtract a multiset from the environment

        The subtraction operation has a condition such that the multiset we
        want to subtract has to be a subset of the environment. If the
        condition is met, then subtraction simply involves the subtraction of
        the multiplicities of the objects in the parameter `multiset` from
        the corresponding objects multiplicity the environment in the case of it
        being in the `objects` multiset. If however, the objects is in the
        `infinite_obj` list, then no subtraction is not necessary, since the
        multiplicity of the given object is infinite in the environment.

        Parameters
        ----------
        multiset : MultiSet
            the multiset we want to subtract from `self`

        Returns
        -------
        MultiSet
            the `self` object we subtracted `multiset` from
        """

        if self.has_subset(multiset):
            for obj, mul in multiset:
                if obj in self.infinite_obj:
                    pass
                else:
                    self[obj] -= mul
                    if self[obj] == 0:
                        del self[obj]
            return self
        else:
            raise InvalidOperationException


class MembraneSignal(QObject):
    """
    A class to represent the signals which can be emitted by the membrane system

    Attributes
    ----------
    sim_over : Signal
        the signal that communicates that the simulation is over
    sim_step_over : Signal
        the signal that communicates that a simulation step is over
    region_dissolved : Signal
         the signal that communicates that a region has dissolved
    obj_changed : Signal
         the signal that communicates that a region's objects have changed
    rules_changed : Signal
         the signal that communicates that a region's rules have changed
    """

    sim_over = Signal(dict)
    sim_step_over = Signal(int)
    region_dissolved = Signal(int)
    obj_changed = Signal(int, str)
    rules_changed = Signal(int, str)


class MembraneSystem(QObject):
    """
    A class to represent the abstract membrane system

    Attributes
    ----------
    tree : MembraneStructure
        the tree structure of the regions in the membrane system
    environment : Environment
        the environment of the membrane system
    step_counter : int
        the number of simulation steps that have occured
    regions : dict
        the dictionary containing the region objects keyed by their identifier
    signal : MembraneSignal
        the objects for containing all the available signals
    """

    def __init__(self,
                 tree=None,
                 regions=None, infinite_obj=None, structure_str=None):
        """
        A function to initialize the membrane system

        Parameters
        ----------
        tree : MembraneStructure, optional
            the tree structure of the regions in the membrane system (default is None)
        regions : dict, optional
            the dictionary containing the regions keyed by their identifier (default is None)
        infinite_obj : list, optional
            the list of objects in the environment with infinite multiplicity (default is None)
        signal : MembraneSignal
            the objects for containing all the available signals
        structure_str : str, optional
            the string used to create the membrane system (default is None)
        """

        self.tree = tree
        self.environment = Environment(infinite_obj=infinite_obj)
        self.step_counter = 0
        self.structure_str = structure_str

        # { region_id : region_obj }
        self.regions: Dict = regions

        self.signal = MembraneSignal()
        for r in self.regions.values():
            r.signal.obj_changed.connect(self.signal.obj_changed.emit)
            r.signal.rules_changed.connect(self.signal.rules_changed.emit)

    # @abc.abstractmethod
    def apply(self, rule, region):
        """
        Abstract function to apply an evolution rule to a region

        Parameters
        ----------
        rule : Rule
            the rule to be applied
        region : Region
            the region that the rule is connected to
        """

        pass

    # @abc.abstractmethod
    def is_applicable(self, rule, region):
        """
        Abstract function to determine whether a rule can be applied to a region

        Parameters
        ----------
        rule : Rule
            the rule to be applied
        region : Region
            the region that the rule is connected to

        Returns
        -------
        bool
            True if it can be applied, False otherwise
        """

        pass

    # @abc.abstractmethod
    def simulate_step(self):
        """
        Abstract function used to simulate a single evolution step in the
        membrane system
        """

        pass

    # @abc.abstractmethod
    def get_result(self):
        """
        Abstract function used to return the result of the calculation
        """

        pass

    @classmethod
    def is_valid_parentheses(cls, m_str):
        """
        A classmethod used to check if the string `m_str` is a valid structure
        for a membrane system

        Membrane systems can easily be represented with between brackets with
        their objects as characters. Nesting them is also possible making it the
        most consise way to describe such systems (rules have to be omitted or
        brought to similar string format)

        Parameters
        ----------
        m_str : str
            the string containing the structure and objects of
            the membrane system

        Returns
        -------
        bool
            True if `m_str` can represent a valid membrane system,
            False otherwise
        """

        open_paren = set(['(', '{', '['])
        close_paren = set([')', '}', ']'])
        stack = []
        pairs = {'}': '{', ')': '(', ']': '['}

        for c in m_str:
            if c in close_paren:
                if not stack:
                    return False
                elif pairs[c] != stack.pop():
                    return False
                else:
                    continue
            if c not in open_paren.union(close_paren):
                continue
            if c in open_paren:
                stack.append(c)
        if not stack:
            return True
        else:
            return False

    # @abc.abstractmethod
    @classmethod
    def create_model_from_str(cls, m_str):
        """
        Abstract method used to create the membrane system corresponding
        to the given string

        Before calling this method, one has to check if the string is valid with
        the function `is_valid_parentheses()`

        Parameters
        ----------
        m_str : str
            the string containing the membrane systems configuration
        """

        pass

    def get_rule_string(self, region_id):
        """
        A function to return the string representation of a region's list of
        rules

        Parameters
        ----------
        region_id : int
            the unique identifier of the region

        Returns
        -------
        str
            the concatenated string of the rules in the region
        """
        return self.regions[region_id].get_rule_string()

    @classmethod
    def is_valid_rule(cls, rule_str):
        """
        Abstract class method used to check if a string is a valid
        representation of a rule

        Parameters
        ----------
        rule_str : str
            the string containing the rule

        Returns
        -------
        bool
            True if it is a valid rule, False otherwise
        """

        pass

    @classmethod
    def string_to_rules(cls, rule_str):
        """
        Abstract class method used to create a list of rules from `rule_str`

        Returns
        -------
        list
            the list of created rules
        """

        pass

    @classmethod
    def parse_rule(cls, rule_str):
        """
        Abstract class method used to parse `rule_str` and create a rule

        Returns
        -------
        Rule
            the rule created by the string
        """

        pass

    @property
    def regions(self):
        """
        A getter method for the membrane system's regions

        Returns
        -------
        dict
            the dictionary containing {region_id : region_obj} pairs
        """

        return self._regions

    @regions.setter
    def regions(self, value):
        """
        The setter method for the membrane system's regions

        Parameters
        ----------
        value : list
            the list containing the new rules
        """

        self._regions = value

    def select_and_apply_rules(self, region):
        indices = list(range(len(region.rules)))
        while indices:
            idx = random.choice(indices)
            if self.is_applicable(region.rules[idx], region):
                self.apply(region.rules[idx], region)
            else:
                indices.remove(idx)

    def get_parent_region(self, region):
        """
        A function used to return a region's parent

        Parameters
        ----------
        region : Region
            the region whose parent needs to be returned

        Returns
        -------
        Region
            the parent region
        """

        region_id = region.id
        self.tree.preorder(self.tree.skin, self.tree.get_parent,
                           lambda x: x.id == region_id)
        result_node = self.tree.result
        return self.regions[result_node.id]

    def get_all_children(self, region):
        """
        A function used to return the children of the given region

        Parameters
        ----------
        region : Region
            the region whose children need to be returned

        Returns
        -------
        list
            the list containing the children
        """

        region_id = region.id
        self.tree.preorder(self.tree.skin, self.tree.get_all_children,
                           lambda x: x.id == region_id)
        result_list = self.tree.result
        return [self.regions[i.id] for i in result_list]

    def get_num_of_children(self, region):
        """
        A function used to return the number of children
        of the given region

        Parameters
        ----------
        region : Region
            the region whose number of children needs to be returned

        Returns
        -------
        int
            the number of children to node has
        """

        region_id = region.id
        self.tree.preorder(self.tree.skin,
                           self.tree.get_num_of_children,
                           lambda x: x.id == region_id)
        return self.tree.result

    def get_child(self, region):
        """
        A function used to return one of the children of the given region

        Parameters
        ----------
        region : Region
            the region whose number of children needs to be returned

        Returns
        -------
        Region
            the child of the region
        """

        region_id = region.id
        self.tree.preorder(self.tree.skin, self.tree.get_all_children,
                           lambda x: x.id == region_id)
        result_list = self.tree.result
        return None if result_list is None else self.regions[
            random.choice(result_list).id]

    def get_root_id(self):
        """
        A function used to return the identifier of the root node in the
        tree structure

        Returns
        -------
        int
            the identifier of the root node
        """

        return self.tree.get_root_id()

    def any_rule_applicable(self):
        """
        A function to check if any rule can be applied in the membrane system

        This is important, because the simulation ends when this condition is
        not met

        Returns
        -------
        bool
            True if there is a rule which can be applied, False otherwise
        """
        for region in self.regions.values():
            for rule in region.rules:
                if self.is_applicable(rule, region):
                    return True
        return False

    def simulate_computation(self):
        """
        A function to run the whole simulation of a membrane system

        Emits `sim_over` signal when there are no possible rules to apply to any
        region
        """

        while self.any_rule_applicable():
            self.simulate_step()
        self.signal.sim_over.emit(self.get_result())
        return self.get_result()

    @classmethod
    def load_from_json_dict(cls, json_dict):
        """
        A class method used to construct a membrane system (or one of its derived
        classes) from a JSON dictionary object

        Since this is a classmethod, this function will work perfectly well with
        subclasses, since each of them have to implement `create_model_from_str`
        and `parse_rule`, in order to be instantiable.

        Parameters
        ----------
        json_dict
            the JSON dictionary containing the configuration of the membrane
            system

        Returns
        -------
        MembraneSystem (or subtype)
            the system constructed from the JSON dictionary
        """

        structure = json_dict["structure"]
        model = cls.create_model_from_str(structure)
        root_id = min(list(map(int, model.regions.keys())))
        for id in json_dict["rules"].keys():
            rule_list = json_dict["rules"][id]
            for rule in rule_list:
                parsed_rule = cls.parse_rule(rule)
                shifted_id = int(id) + root_id
                model.regions[shifted_id].add_rule(parsed_rule)
        return model

    def create_json_dict(self):
        """
        A function used to extract the information from the membrane system that
        is essential for recreating

        Returns
        -------
        dict
            the dictionary that will be used to serialize the system
        """

        result = {}
        result["type"] = self.__class__.__name__
        result["structure"] = self.structure_str
        result["rules"] = {}
        for r in self.regions.values():
            for rule in r.rules:
                result["rules"][r.id - self.get_root_id()] = []

        for r in self.regions.values():
            for rule in r.rules:
                result["rules"][r.id - self.get_root_id()].append(str(rule))
        return result

    def save(self, path):
        """
        A function responsible for saving the state of the membrane system to
        the given path

        Parameters
        ----------
        path : str
            the string containing the file path
        """

        json_dict = self.create_json_dict()
        with open(path, 'w') as save_file:
            json.dump(json_dict, save_file)

    @classmethod
    def load(cls, json_dict):
        """
        A class method used for instantiating a membrane system from a JSON
        dictionary

        The membrane system will be of type that is specified in the `type` pair
        contained in the dictionary

        Parameters
        ----------
        json_dict : dict
            the dictionary containing information for the membrane system's
            creation

        Returns
        -------
        MembraneSystem (or any of it's derived classes)
            the system created by the dictionary
        """
        return cls.load_from_json_dict(json_dict)
