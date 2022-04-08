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
    def __init__(self, tree=None,
                 regions=None, infinite_obj=None, out_id=None):
        MembraneSystem.__init__(self, tree=tree, regions=regions,
                                infinite_obj=infinite_obj)
        assert out_id is not None
        self.output_id = out_id

    def __repr__(self):
        return f'Env:{self.environment} {self.regions.__repr__()}'

    def apply(self, rule, region):
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
        else:
            region.objects -= rule.exported_obj
            region.new_objects += rule.imported_obj
            parent = self.get_parent_region(region)
            parent.new_objects += rule.exported_obj
            parent.objects -= rule.imported_obj

    def is_applicable(self, rule, region):
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
        if not self.any_rule_applicable():
            self.signal.sim_over.emit()
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
        return self.regions[self.output_id]

    @classmethod
    def create_model_from_str(cls, m_str):
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
        return SymportAntiport(tree=structure, regions=regions)

    @classmethod
    def is_valid_rule(cls, rule_str):
        rule_str = rule_str.replace(" ", "")
        return re.match(
            r'^(IN:\s*[a-z]+\s*$|OUT:\s*[a-z]+\s*$|(\s*IN:\s*\w+\s*OUT:\s*\w+\s*|\s*OUT:\s*[a-z]+\s*IN:\s*\w+\s*))',
            rule_str)

    @classmethod
    def string_to_rules(cls, rules_str):
        result_rules = []
        split_str = rules_str.split("\n")
        for rule in split_str:
            result_rules.append(SymportAntiport.parse_rule(rule))
        return result_rules

    @classmethod
    def parse_rule(cls, rule_str):
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
