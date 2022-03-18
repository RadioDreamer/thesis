import random

from MembraneSystem import MembraneSystem
from MultiSet import MultiSet
from Rule import (
    SymportRule,
    TransportationRuleType
)


class SymportAntiport(MembraneSystem):
    def __repr__(self):
        return f'Env:{self.environment} {self.regions.__repr__()}'

    def __init__(self, is_dissolving=False, is_priority=False, tree=None,
                 regions=None, infinite_obj=None, out_id=None):
        MembraneSystem.__init__(self, tree=tree, regions=regions,
                                infinite_obj=infinite_obj)
        assert out_id is not None
        self.output_id = out_id

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
        shuffle_regions = list(self.regions.values())
        random.shuffle(shuffle_regions)
        for region in shuffle_regions:
            self.select_and_apply_rules(region)
        for region in self.regions.values():
            region.objects += region.new_objects
            region.new_objects = MultiSet()

    def get_result(self):
        return self.regions[self.output_id]

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
