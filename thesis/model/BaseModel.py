from MembraneSystem import MembraneSystem
from Rule import (
    PriorityRule,
    BaseModelRule,
    DissolvingRule,
    Direction
)

from MultiSet import MultiSet


class BaseModel(MembraneSystem):
    def simulate_step(self):
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
