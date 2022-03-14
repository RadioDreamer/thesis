import abc
from typing import Dict


class MembraneSystem(metaclass=abc.ABCMeta):
    def __init__(self, is_dissolving=False, is_priority=False, tree=None,
                 regions=None):
        self.is_dissolving = is_dissolving
        self.is_priority = is_priority
        self.tree = tree

        # { region_id : region_object }
        self.regions: Dict = regions

    @abc.abstractmethod
    def apply(self):
        pass

    def select_and_apply_rules(self, region):
        condition = True
        while condition:
            can_apply = False
            for rule in region.rules:
                if self.is_applicable(rule, region):
                    can_apply = True
                    self.apply(rule, region)
            condition = can_apply

    def get_parent_region(self, region_id):
        pass

    def simulate_step(self):
        for region in self.regions.values():
            self.select_and_apply_rules(region)
        for region in self.regions.values():
            region.objects += region.new_objects
            if region.is_dissolving:
                self.dissolve_region(region)

    def any_rule_applicable(self):
        for region in self.regions.values():
            for rule in region.rules():
                if self.is_applicable(rule, region):
                    return True
        return False
    
    def simulate_computation(self):
        while self.any_rule_applicable():
            self.simulate_step()
