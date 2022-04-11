import random
from typing import Dict, List
from MultiSet import MultiSet
from MultiSet import InvalidOperationException
from PySide6.QtCore import QObject, Signal


class InvalidArgumentException(Exception):
    pass


class Environment(MultiSet):
    def __init__(self, objects=None, infinite_obj=None):
        super().__init__(objects)
        self.infinite_obj = set(infinite_obj) if infinite_obj else None
        if infinite_obj is not None:
            delete = [obj for obj in self.objects if obj in infinite_obj]
            for obj in delete:
                del self[obj]

    def has_subset(self, multiset):
        for obj, mul in multiset:
            if obj in self and self[obj] >= mul:
                pass
            elif self.infinite_obj and obj in self.infinite_obj:
                pass
            else:
                return False
        return True

    def __add__(self, multiset):
        raise InvalidOperationException

    def __sub__(self, multiset):
        raise InvalidOperationException

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


class MembraneSignal(QObject):
    sim_over = Signal(dict)
    sim_step_over = Signal(int)
    region_dissolved = Signal(int)
    obj_changed = Signal(int, str)
    rules_changed = Signal(int, str)


class MembraneSystem(QObject):
    def __init__(self,
                 tree=None,
                 regions=None, infinite_obj=None):
        self.tree = tree
        self.environment = Environment(infinite_obj=infinite_obj)
        self.step_counter = 0

        # { region_id : region_obj }
        self.regions: Dict = regions

        self.signal = MembraneSignal()
        for r in self.regions.values():
            r.signal.obj_changed.connect(self.signal.obj_changed.emit)
            r.signal.rules_changed.connect(self.signal.rules_changed.emit)

    # @abc.abstractmethod
    def apply(self, rule, region):
        pass

    # @abc.abstractmethod
    def is_applicable(self, rule, region):
        pass

    # @abc.abstractmethod
    def simulate_step(self):
        pass

    # @abc.abstractmethod
    def get_result(self):
        pass

    @classmethod
    def is_valid_parentheses(cls, m_str):
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
        pass

    def get_rule_string(self, region_id):
        return self.regions[region_id].get_rule_string()

    @classmethod
    def is_valid_rule(cls, rule_str):
        pass

    @classmethod
    def string_to_rules(cls):
        pass

    @classmethod
    def parse_rule(cls):
        pass

    @property
    def regions(self):
        return self._regions

    @regions.setter
    def regions(self, value):
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

    def get_num_of_children(self, region):
        region_id = region.id
        self.tree.preorder(self.tree.skin,
                           self.tree.get_num_of_children,
                           lambda x: x.id == region_id)
        return self.tree.result

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
        self.signal.sim_over.emit(self.get_result())
        return self.get_result()

# class MembraneSystem(metaclass=abc.ABCMeta):
#     def __init__(self, is_dissolving=False, is_priority=False, tree=None,
#                  regions=None, infinite_obj=None):
#         self.is_dissolving = is_dissolving
#         self.is_priority = is_priority
#         self.tree = tree
#         self.environment = Environment(infinite_obj=infinite_obj)
#
#         # { region_id : region_obj }
#         self.regions: Dict = regions
#
#     @abc.abstractmethod
#     def apply(self, rule, region):
#         pass
#
#     @abc.abstractmethod
#     def is_applicable(self, rule, region):
#         pass
#
#     @abc.abstractmethod
#     def simulate_step(self):
#         pass
#
#     @abc.abstractmethod
#     def get_result(self):
#         pass
#
#     @classmethod
#     @abc.abstractmethod
#     def create_from_str(cls, m_str):
#         pass
#
#     @classmethod
#     def is_valid_parentheses(cls, m_str):
#         open_paren = set(['(', '{', '['])
#         close_paren = set([')', '}', ']'])
#         stack = []
#         pairs = {'}': '{', ')': '(', ']': '['}
#
#         for c in m_str:
#             if c not in open_paren.union(close_paren):
#                 continue
#             if c in open_paren:
#                 stack.append(c)
#             if c in close_paren:
#                 if not stack:
#                     return False
#                 elif pairs[c] != stack.pop():
#                     return False
#                 else:
#                     continue
#         if not stack:
#             return True
#         else:
#             return False
#
#     @property
#     def regions(self):
#         return self._regions
#
#     @regions.setter
#     def regions(self, value):
#         self._regions = value
#
#     def add_rule(self, region, rule):
#         self.regions[region.id].rules.append(rule)
#
#     def select_and_apply_rules(self, region):
#         indices = list(range(len(region.rules)))
#         while indices:
#             idx = random.choice(indices)
#             if self.is_applicable(region.rules[idx], region):
#                 self.apply(region.rules[idx], region)
#             else:
#                 indices.remove(idx)
#
#     # def select_and_apply_rules(self, region):
#     #     condition = True
#     #     while condition:
#     #         can_apply = False
#     #         # This needs to be non-deterministic
#     #         for rule in random.shuffle(region.rules):
#     #             if self.is_applicable(rule, region):
#     #                 can_apply = True
#     #                 self.apply(rule, region)
#     #         condition = can_apply
#
#     def get_parent_region(self, region):
#         region_id = region.id
#         self.tree.preorder(self.tree.skin, self.tree.get_parent,
#                            lambda x: x.id == region_id)
#         result_node = self.tree.result
#         return self.regions[result_node.id]
#
#     def get_all_children(self, region):
#         region_id = region.id
#         self.tree.preorder(self.tree.skin, self.tree.get_all_children,
#                            lambda x: x.id == region_id)
#         result_list = self.tree.result
#         return [self.regions[i.id] for i in result_list]
#
#     def get_num_of_children(self, region):
#         region_id = region.id
#         self.tree.preorder(self.tree.skin, self.tree.get_num_of_children,
#                            lambda x: x.id == region_id)
#         return self.tree.result
#
#     def get_child(self, region):
#         region_id = region.id
#         self.tree.preorder(self.tree.skin, self.tree.get_all_children,
#                            lambda x: x.id == region_id)
#         result_list = self.tree.result
#         return None if result_list is None else self.regions[
#             random.choice(result_list).id]
#
#     def get_root_id(self):
#         return self.tree.get_root_id()
#
#     def any_rule_applicable(self):
#         for region in self.regions.values():
#             for rule in region.rules:
#                 if self.is_applicable(rule, region):
#                     return True
#         return False
#
#     def simulate_computation(self):
#         while self.any_rule_applicable():
#             self.simulate_step()
#         return self.get_result()
