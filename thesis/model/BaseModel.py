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
    @classmethod
    def create_from_str(cls, m_str):
        if not MembraneSystem.is_valid_parentheses(m_str):
            raise InvalidArgumentException

        root_node = None
        current_node = None

        regions = {}

        for c in m_str:
            if c == ' ':
                continue
            elif c in ['[', '{', '(']:
                if root_node is None:
                    root_node = Node()
                    regions[root_node.id] = Region(root_node.id)
                    current_node = root_node
                else:
                    new_node = Node()
                    regions[new_node.id] = Region(new_node.id)
                    current_node.add_child(new_node)
                    current_node = new_node
            elif c in [']', '}', ')']:
                current_node = current_node.parent
            else:
                regions[current_node.id].objects.add_object(c)
        structure = MembraneStructure(root_node)
        return BaseModel(tree=structure, regions=regions)

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
    def is_valid_rule(cls, rule_str):
        return re.match(
            r'\w*\s+(|#)->\s+(IN|in):\s*\w*\s*(OUT|out):\s*\w*\s*(HERE|here):\w*\s*(|>\s*\w*\s*(|#)->\s*(IN|in):\s*\w*\s*(OUT|out):\s*\w*\s*(HERE|here):)',
            rule_str)

    @classmethod
    def string_to_rules(cls):
        result_rules = None

        return result_rules

    def dissolve_region(self, region):
        self.get_parent_region(region).objects += region.objects
        self.tree.preorder(self.tree.skin, self.tree.remove_node,
                           lambda x: x.id == region.id)
        del self.regions[region.id]

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
                self.tree.preorder(self.tree.skin,
                                   self.tree.get_num_of_children,
                                   lambda x: x.id == region.id)
                num_of_children = self.tree.result
                if rule.has_in_object() and num_of_children == 0:
                    return False
                else:
                    return region.objects.has_subset(rule.left_side)

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

    def get_result(self):
        return self.environment.objects

    @classmethod
    def is_valid_rule(cls, rule_str):
        return True
