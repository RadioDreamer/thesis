import random
import re

from MembraneSystem import MembraneSystem, InvalidArgumentException
from MultiSet import MultiSet
from Rule import (
    SymportRule,
    TransportationRuleType
)
from MembraneStructure import MembraneStructure, Node
from Region import Region


class SymportAntiport(MembraneSystem):
    """
    A class to represent the symport antiport invariant of the membrane systems

    In this type of system, the rules can be of three types:
    `ANTIPORT` means that objects travel both in and out of the region
    `SYMPORT_IN` means that objects travel only into the region
    `SYMPORT_OUT` means that objects travel only out of the region

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
    structure_str : str, optional
        the string used to create the membrane system (default is None)
    out_id : int
        the special region's identifier which contains the result of the
        computation
    """

    def __init__(self, tree=None,
                 regions=None, infinite_obj=None, structure_str=None,
                 out_id=None):
        """
        A function used to initalize a symport/antiport system

        Parameters
        ----------
        tree : MembraneStructure
            the tree structure of the regions in the membrane system
        regions : dict
            the dictionary containing the regions keyed by their identifier
        infinite_obj : list
            the list of objects in the environment with infinite multiplicity
        out_id : int
            the identifier of the output region
        """

        MembraneSystem.__init__(self, tree=tree, regions=regions,
                                infinite_obj=infinite_obj,
                                structure_str=structure_str)
        assert out_id is not None
        self.output_id = out_id

    def __repr__(self):
        """
        A function which generates the instance's representation

        Returns
        -------
        str
            the string containing the configuration of the system
        """

        return f'Env:{self.environment} {self.regions.__repr__()}'

    def apply(self, rule, region):
        """
        A function that overrides the base class's `apply`

        If there are exported objects within the region, we simply remove them
        and add them to the parent region (since rules can always be in the form
        of `IN: ___ OUT: ____`, thus if the rule is assigned to `region`, objects
        can only travel outwards from it. The imported objects are removed from
        the parent's objects and added to this region's objects. If the rule is
        `SYMPORT_IN` or `SYMPORT_OUT` then only one of the two interactions will
        happen.

        Parameters
        ----------
        rule : SymportRule
            the rule to be applied
        region : Region
            the region that the rule is assigned to
        """

        if rule.rule_type == TransportationRuleType.SYMPORT_IN:
            if region.id == self.get_root_id():
                self.environment -= rule.imported_obj
            else:
                self.get_parent_region(region).objects -= rule.imported_obj
            region.new_objects += rule.imported_obj
        elif rule.rule_type == TransportationRuleType.SYMPORT_OUT:
            region.objects -= rule.exported_obj
            if self.get_root_id() == region.id:
                self.environment += rule.exported_obj
            else:
                self.get_parent_region(region).new_objects += rule.exported_obj
        elif rule.rule_type == TransportationRuleType.ANTIPORT:
            if region.id == self.get_root_id():
                self.environment += rule.exported_obj
                self.environment -= rule.imported_obj
                region.objects -= rule.exported_obj
                region.objects += rule.imported_obj
            else:
                region.objects -= rule.exported_obj
                region.new_objects += rule.imported_obj
                parent = self.get_parent_region(region)
                parent.new_objects += rule.exported_obj
                parent.objects -= rule.imported_obj

    def is_applicable(self, rule, region):
        """
        A function that checks if a rule can be applied to a region

        Parameters
        ----------
        rule : SymportRule
            the rule to be applied
        region : Region
            the region that the rule is assigned to

        Returns
        -------
        bool
            True if it can be applied, False otherwise
        """

        assert isinstance(rule, SymportRule)
        if rule.rule_type == TransportationRuleType.ANTIPORT:
            if self.get_root_id() == region.id:
                if self.environment.has_subset(
                        rule.imported_obj) and region.objects.has_subset(
                    rule.exported_obj):
                    return True
                else:
                    return False
            else:
                if region.objects.has_subset(
                        rule.exported_obj) and self.get_parent_region(
                    region).objects.has_subset(rule.imported_obj):
                    return True
                else:
                    return False
        elif rule.rule_type == TransportationRuleType.SYMPORT_IN:
            if self.get_root_id() == region.id:
                if self.environment.has_subset(rule.imported_obj):
                    return True
            else:
                if self.get_parent_region(region).objects.has_subset(
                        rule.imported_obj):
                    return True
                else:
                    return False
        elif rule.rule_type == TransportationRuleType.SYMPORT_OUT:
            if region.objects.has_subset(rule.exported_obj):
                return True
            else:
                return False

    def simulate_step(self):
        # TODO: rendszerszinten nézni a szabályokat, nem elég régiónként
        #  végigmenni

        """
        A function to simulate a single evolution step in the membrane system

        The order in which the regions are selected has to be random, in order
        to guarantee non-determinisic behaviour
        """

        if not self.any_rule_applicable():
            self.signal.sim_over.emit(self.get_result())
            return
        shuffle_regions = list(self.regions.values())
        random.shuffle(shuffle_regions)
        for region in shuffle_regions:
            self.select_and_apply_rules(region)
        for region in self.regions.values():
            region.objects += region.new_objects
            region.new_objects = MultiSet()
        self.step_counter += 1
        self.signal.sim_step_over.emit(self.step_counter)

    def get_result(self):
        """
        A function to return the result of the calculation

        Only returns the correct output if called after emitting `sim_over`

        For the symport/antiport system, the result of the simulation is the
        state of the region with `out_id` identifier

        Returns
        -------
        MultiSet
            the objects in the region with identifier `out_id`
        """

        return self.regions[self.output_id].objects

    @classmethod
    def create_model_from_str(cls, m_str):
        """
       A static method responsible for creating a `SymportAntiport` instance
       from a string

       Parameters
       ----------
       m_str : str
           the string containing the configuration of the model

       Returns
       -------
       SymportAntiport
           the model corresponding to the string
       """

        if not MembraneSystem.is_valid_parentheses(m_str):
            raise InvalidArgumentException
        root_node = None
        current_node = None

        output_id = None
        closing_brackets = [']', '}', ')']
        opening_brackets = ['[', '{', '(']

        infite_obj = []
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
                if root_node is None:
                    infite_obj.append(c)
                else:
                    regions[current_node.id].objects.add_object(c)
            elif c == '#':
                output_id = current_node.id
            else:
                raise InvalidArgumentException

        structure = MembraneStructure(root_node)
        return SymportAntiport(tree=structure, regions=regions,
                               out_id=output_id, infinite_obj=infite_obj,
                               structure_str=m_str)

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
            r'^(IN:\s*[a-z]+\s*$|OUT:\s*[a-z]+\s*$|(\s*IN:\s*\w+\s*OUT:\s*\w+\s*|\s*OUT:\s*[a-z]+\s*IN:\s*\w+\s*))',
            rule_str)

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
            result_rules.append(SymportAntiport.parse_rule(rule))
        return result_rules

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

        exp_obj = None
        imp_obj = None
        rule_str = rule_str.replace(" ", "")
        contains_in = 'IN:' in rule_str
        contains_out = 'OUT:' in rule_str
        if contains_in and contains_out:
            split_list = rule_str.replace('IN:', '|').replace('OUT:',
                                                              '|').split('|')[
                         1:]
            if rule_str.index('IN:') < rule_str.index('OUT:'):
                imp_obj = MultiSet.string_to_multiset(split_list[0]).objects
                exp_obj = MultiSet.string_to_multiset(split_list[1]).objects
                return SymportRule(TransportationRuleType.ANTIPORT,
                                   imported_obj=imp_obj, exported_obj=exp_obj)
            else:
                exp_obj = MultiSet.string_to_multiset(split_list[0]).objects
                imp_obj = MultiSet.string_to_multiset(split_list[1]).objects
                return SymportRule(TransportationRuleType.ANTIPORT,
                                   imported_obj=imp_obj, exported_obj=exp_obj)
        elif contains_in:
            imp_obj = MultiSet.string_to_multiset(rule_str[3:]).objects
            return SymportRule(TransportationRuleType.SYMPORT_IN,
                               imported_obj=imp_obj)
        elif contains_out:
            exp_obj = MultiSet.string_to_multiset(rule_str[4:]).objects
            return SymportRule(TransportationRuleType.SYMPORT_OUT,
                               exported_obj=exp_obj)
        else:
            raise InvalidArgumentException

    # Version without removing spaces before checking regex
    #    @classmethod
    #    def is_valid_rule(cls, rule_str):
    #        return re.match(
    #            r'^(IN:\s*[a-z]+\s*$|OUT:\s*[a-z]+\s*$|(\s*IN:\s*\w+\s*OUT:\s*\w+\s*|\s*OUT:\s*[a-z]+\s*IN:\s*\w+\s*))',
    #            rule_str)
