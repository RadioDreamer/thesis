import abc
import random
from typing import Dict, List
from MultiSet import MultiSet
from MultiSet import InvalidOperationException


class Environment(MultiSet):
    def __init__(self, objects=None, infinite_obj=None):
        super().__init__(objects)
        self.infinite_obj: List = infinite_obj
        if infinite_obj is not None:
            delete = [obj for obj in self.objects if obj in infinite_obj]
            for obj in delete:
                del self[obj]

    def has_subset(self, multiset):
        for obj, mul in multiset:
            if obj in self and self[obj] >= mul:
                pass
            elif obj in self.infinite_obj:
                pass
            else:
                return False
        return True

    def __iadd__(self, multiset):
        for obj, mul in multiset:
            if obj in self.infinite_obj:
                pass
            elif obj in self.objects:
                self[obj] += mul
            else:
                self[obj] = mul

        return self

    def __isub__(self, multiset):
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


class MembraneSystem(metaclass=abc.ABCMeta):
    def __init__(self, is_dissolving=False, is_priority=False, tree=None,
                 regions=None, infinite_obj=None):
        self.is_dissolving = is_dissolving
        self.is_priority = is_priority
        self.tree = tree
        self.environment = Environment(infinite_obj=infinite_obj)

        # { region_id : region_obj }
        self.regions: Dict = regions

    @abc.abstractmethod
    def apply(self, rule, region):
        pass

    @abc.abstractmethod
    def is_applicable(self, rule, region):
        pass

    @abc.abstractmethod
    def simulate_step(self):
        pass

    @abc.abstractmethod
    def get_result(self):
        pass

    def select_and_apply_rules(self, region):
        indices = list(range(len(region.rules)))
        while indices:
            idx = random.choice(indices)
            if self.is_applicable(region.rules[idx], region):
                self.apply(region.rules[idx], region)
            else:
                indices.remove(idx)

    # def select_and_apply_rules(self, region):
    #     condition = True
    #     while condition:
    #         can_apply = False
    #         # This needs to be non-deterministic
    #         for rule in random.shuffle(region.rules):
    #             if self.is_applicable(rule, region):
    #                 can_apply = True
    #                 self.apply(rule, region)
    #         condition = can_apply

    def get_parent_region(self, region):
        region_id = region.id
        self.tree.preorder(self.tree.skin, self.tree.get_parent,
                           lambda x: x.id == region_id)
        result_node = self.tree.result
        return self.regions[result_node.id]

    def get_all_children(self, region):
        region_id = region.id
        self.tree.preorder(self.tree.skin, self.tree.get_all_children,
                           lambda x: x.id == region_id)
        result_list = self.tree.result
        return [self.regions[i.id] for i in result_list]

    def get_child(self, region):
        region_id = region.id
        self.tree.preorder(self.tree.skin, self.tree.get_all_children,
                           lambda x: x.id == region_id)
        result_list = self.tree.result
        return None if result_list is None else self.regions[
            random.choice(result_list).id]

    def get_root_id(self):
        return self.tree.get_root_id()

    def any_rule_applicable(self):
        for region in self.regions.values():
            for rule in region.rules:
                if self.is_applicable(rule, region):
                    return True
        return False

    def simulate_computation(self):
        while self.any_rule_applicable():
            self.simulate_step()
        return self.get_result()
