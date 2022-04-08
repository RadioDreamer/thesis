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
    def apply(self, rule, region):
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
        if not self.any_rule_applicable():
            self.signal.sim_over.emit()
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
            self.dissolve_region(region)
            self.signal.region_dissolved.emit(region.id)

        self.step_counter += 1
        self.signal.sim_step_over.emit(self.step_counter)

    def get_result(self):
        return self.environment.objects

    def dissolve_region(self, region):
        self.get_parent_region(region).objects += region.objects
        self.tree.preorder(self.tree.skin, self.tree.remove_node,
                           lambda x: x.id == region.id)
        del self.regions[region.id]

    def select_and_apply_rules(self, region):
        indices = list(range(len(region.rules)))
        while indices:
            idx = random.choice(indices)
            if self.is_applicable(region.rules[idx], region):
                if isinstance(region.rules[idx], DissolvingRule):
                    indices.remove(idx)
                self.apply(region.rules[idx], region)
            else:
                indices.remove(idx)

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
        return BaseModel(tree=structure, regions=regions)

    @classmethod
    def is_valid_rule(cls, rule_str):
        rule_str = rule_str.replace(" ", "")
        return re.match(
            r'[a-z]+->(|#)(IN|in):[a-z]*(OUT|out):[a-z]*(HERE|here):[a-z]*(|>[a-z]+(|#)->(IN|in):[a-z]*(OUT|out):[a-z]*(HERE|here):)',
            rule_str)

    @classmethod
    def parse_rule(cls, rule_str):
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
            print(right_side_list)
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
            # rs_list = list(filter(''.__ne__, rs_list))
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
        result_rules = []
        split_str = rules_str.split("\n")
        for rule in split_str:
            result_rules.append(BaseModel.parse_rule(rule))
        return result_rules

    #    @classmethod
    #    def is_valid_rule(cls, rule_str):
    #        return re.match(
    #            r'[a-z]+\s+->(|#)\s+(IN|in):\s*\w*\s*(OUT|out):\s*\w*\s*(HERE|here):\w*\s*(|>\s*\w*\s*(|#)->\s*(IN|in):\s*\w*\s*(OUT|out):\s*\w*\s*(HERE|here):)',
    #            rule_str)
