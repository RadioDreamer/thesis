import copy
import random
import re
from MembraneSystem import MembraneSystem
from Rule import (
    PriorityRule,
    BaseModelRule,
    DissolvingRule,
    Direction
)

from MultiSet import MultiSet
from MembraneSystem import InvalidArgumentException
from MembraneStructure import Node, MembraneStructure
from Region import Region


class BaseModel(MembraneSystem):
    """
    A class to represent the base model of a membrane system

    Attributes
    ----------
    tree : MembraneStructure
        the tree structure of the regions in the membrane system
    environment : Environment
        the environment of the membrane system
    step_counter : int
        the number of simulation steps that have occurred since generation
    regions : dict
        the dictionary containing the region objects keyed by their identifier
    signal : MembraneSignal
        the objects for containing all the available signals
    structure_str : str, optional
        the string used to create the membrane system (default is None)
    """

    def __init__(self, **kwargs):
        """
        A function used to initialize the membrane system

        Essentially calls the base class's `__init__`
        """

        super().__init__(**kwargs)

    def apply(self, rule, region):
        """
        A function that overrides the base class's `apply`

        Parameters
        ----------
        rule : Rule
            the rule that is to be applied
        region : Region
            the region on which the rule is to be applied
        """

        if isinstance(rule, PriorityRule):
            if self.is_applicable(rule.strong_rule, region):
                rule = rule.strong_rule
            else:
                rule = rule.weak_rule

        region.objects -= rule.left_side

        for (obj, direction), mul in rule.right_side:
            if direction == Direction.HERE:
                region.new_objects.add_object(obj, mul)
            elif direction == Direction.OUT:
                if self.tree.get_root_id() == region.id:
                    self.environment.add_object(obj, mul)
                else:
                    self.get_parent_region(region).new_objects.add_object(obj,
                                                                          mul)
            elif direction == Direction.IN:
                self.get_child(region).new_objects.add_object(obj, mul)
        if isinstance(rule, DissolvingRule):
            region.is_dissolving = True

    def is_applicable(self, rule, region):
        """
        A function to check whether a rule can applied to a region

        Parameters
        ----------
        rule : Rule
            the rule to be checked
        region : Region
            the region that the rule acts on

        Returns
        -------
        bool
            True if the rule can be applied, False otherwise
        """

        if isinstance(rule, PriorityRule):
            return self.is_applicable(rule.strong_rule,
                                      region) or self.is_applicable(
                rule.weak_rule, region)
        elif isinstance(rule, BaseModelRule) or isinstance(rule,
                                                           DissolvingRule):
            if self.tree.get_root_id() == region.id and isinstance(rule,
                                                                   DissolvingRule):
                return False
            else:
                num_of_children = self.get_num_of_children(region)
                if rule.has_in_object() and num_of_children == 0:
                    return False
                else:
                    return region.objects.has_subset(rule.left_side)

    def simulate_step(self):
        """
        A function to simulate a single evolution step in the membrane system

        During on step there may be dissolving regions, which are dealt with
        after going through each region

        Increases the `step_counter` variable by 1

        Emits `region_dissolved(int)` and `sim_step_over`
        """

        if not self.any_rule_applicable():
            self.signal.sim_over.emit([self.get_result()])
            return
        for region in self.regions.values():
            self.select_and_apply_rules(region)
        dissolving_regions = []
        for region in self.regions.values():
            region.objects += region.new_objects
            region.new_objects = MultiSet()
            if region.is_dissolving:
                dissolving_regions.append(region)
        for region in dissolving_regions:
            self.signal.region_dissolved.emit(region.id)
            self.dissolve_region(region)

        self.step_counter += 1
        self.signal.sim_step_over.emit(self.step_counter)

    def get_result(self):
        """
        A function to return the result of the calculation

        Only returns the correct output if called after emitting `sim_over`

        For the base model, the result of the simulation is the environment's
        state

        Returns
        -------
        MultiSet
            the objects in the environment
        """

        return self.environment.objects

    @classmethod
    def copy_system(cls, ms):
        """
        A class method to deep copy a base model object

        Since a QObject subclass cannot be serialized, we can copy the object
        by deep copying everything that is needed to construct the new object

        Parameters
        ----------
        ms : BaseModel
            the membrane system to be copied

        Returns
        -------
        BaseModel
            the deep copy of the model
        """

        assert isinstance(ms, BaseModel)
        tree = copy.deepcopy(ms.tree)
        env = copy.deepcopy(ms.environment)
        structure_str = copy.deepcopy(ms.structure_str)

        regions_dict = {k: [None, None] for k in ms.regions.keys()}
        for r_id, rule in ms.regions.items():
            regions_dict[r_id][0] = copy.deepcopy(ms.regions[r_id].objects)
            regions_dict[r_id][1] = copy.deepcopy(ms.regions[r_id].rules)

        regions = {r_id: Region(r_id, l[0], l[1]) for r_id, l in
                   regions_dict.items()}
        copy_model = BaseModel(tree=tree, regions=regions,
                               structure_str=structure_str)
        copy_model.environment = env
        return copy_model

    def dissolve_region(self, region):
        """
        A function used to handle the dissolving of the given region

        The dissolving regions objects will travel to it's parent region. The
        dissolving region's children will have the same parent as the
        dissolving region one.

        Parameters
        ----------
        region : Region
            the region currently dissolving
        """

        self.get_parent_region(region).objects += region.objects
        self.tree.preorder(self.tree.skin, self.tree.remove_node,
                           lambda x: x.id == region.id)
        del self.regions[region.id]

    def select_and_apply_rules(self, region):
        """
        A function that is responsible for selecting and applying rules in a
        region

        The rules are always chosen non-deterministically

        Parameters
        ----------
        region : Region
            the region in which rules can be chosen and applied
        """

        indices = list(range(len(region.rules)))
        while indices:
            idx = random.choice(indices)
            if self.is_applicable(region.rules[idx], region):
                self.apply(region.rules[idx], region)
            else:
                indices.remove(idx)

    @staticmethod
    def create_model_from_str(m_str):
        """
        A static method responsible for creating a `BaseModel` instance from a
        string

        Parameters
        ----------
        m_str : str
            the string containing the configuration of the base model

        Returns
        -------
        BaseModel
            the base model corresponding to the string
        """

        if not MembraneSystem.is_valid_parentheses(m_str):
            raise InvalidArgumentException

        root_node = None
        current_node = None

        closing_brackets = [']', '}', ')']
        opening_brackets = ['[', '{', '(']
        regions = {}
        for c in m_str:
            if c == ' ':
                continue
            elif c in opening_brackets:
                if root_node is None:
                    root_node = Node()
                    regions[root_node.id] = Region(root_node.id)
                    current_node = root_node
                else:
                    new_node = Node()
                    regions[new_node.id] = Region(new_node.id)
                    current_node.add_child(new_node)
                    current_node = new_node
            elif c in closing_brackets:
                current_node = current_node.parent
            elif re.match('[a-z]', c):
                regions[current_node.id].objects.add_object(c)
            else:
                raise InvalidArgumentException
        structure = MembraneStructure(root_node)

        result = BaseModel(tree=structure, regions=regions, structure_str=m_str)
        return result

    @classmethod
    def is_valid_rule(cls, rule_str):
        """
        A class method responsible for determining whether a string contains a
        valid configuration for a rule

        Parameters
        ----------
        rule_str : str
            the string containing the rule

        Returns
        -------
        bool
            True if the string contains a valid rule, False otherwise
        """

        rule_str = rule_str.replace(" ", "")
        return re.match(
            r'[a-z]+->(|#)(IN|in):[a-z]*(OUT|out):[a-z]*(HERE|here):[a-z]*(|>[a-z]+(|#)->(IN|in):[a-z]*(OUT|out):[a-z]*(HERE|here):)',
            rule_str)

    @classmethod
    def parse_rule(cls, rule_str):
        """
        A class method for parsing a string into a rule

        Parameters
        ----------
        rule_str : str
            the string containing the rule

        Returns
        -------
        Rule
            the rule that the string corresponds to
        """

        rule_str = rule_str.replace(" ", "")
        if rule_str.count('>') == 3:
            first = rule_str.index('>')
            second = rule_str[first + 1:].index('>') + first + 1
            return PriorityRule(BaseModel.parse_rule(rule_str[:second]),
                                BaseModel.parse_rule(rule_str[second + 1:]))
        elif '#' in rule_str:
            left_side_end = rule_str.index('-')
            left_side = MultiSet.string_to_multiset(rule_str[:left_side_end])

            right_side_list = rule_str[rule_str.index('#') + 1:]
            right_side_list = right_side_list.replace('IN:', '|').replace(
                'OUT:', '|').replace(
                'HERE:',
                '|').split(
                '|')[1:]
            in_obj = MultiSet.string_to_multiset(right_side_list[0])
            out_obj = MultiSet.string_to_multiset(right_side_list[1])
            here_obj = MultiSet.string_to_multiset(right_side_list[2])
            right_side = {}
            for obj, mul in in_obj:
                right_side[(obj, Direction.IN)] = mul
            for obj, mul in out_obj:
                right_side[(obj, Direction.OUT)] = mul
            for obj, mul in here_obj:
                right_side[(obj, Direction.HERE)] = mul
            return DissolvingRule(left_side, right_side)
        else:
            left_side_end = rule_str.index('-')
            left_side = MultiSet.string_to_multiset(rule_str[:left_side_end])
            right_side_list = rule_str[rule_str.index('>') + 1:]
            rs_list = right_side_list.replace('IN:', '').replace('OUT:',
                                                                 '|').replace(
                'HERE:',
                '|').split(
                '|')
            in_obj = MultiSet.string_to_multiset(rs_list[0])
            out_obj = MultiSet.string_to_multiset(rs_list[1])
            here_obj = MultiSet.string_to_multiset(rs_list[2])
            right_side = {}
            for obj, mul in in_obj:
                right_side[(obj, Direction.IN)] = mul
            for obj, mul in out_obj:
                right_side[(obj, Direction.OUT)] = mul
            for obj, mul in here_obj:
                right_side[(obj, Direction.HERE)] = mul

            return BaseModelRule(left_side, right_side)

    @classmethod
    def string_to_rules(cls, rules_str):
        """
        A class method which creates a list of rules from a string

        The rules in the string must be separated by '\n'

        Parameters
        ----------
        rules_str : str
            the string describing a number of rules

        Returns
        -------
        list
            the list containing the parsed rules
        """

        result_rules = []
        split_str = rules_str.split("\n")
        for rule in split_str:
            result_rules.append(BaseModel.parse_rule(rule))
        return result_rules

