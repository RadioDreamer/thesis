import abc
from enum import Enum
from MultiSet import MultiSet
from typing import Dict


class Direction(Enum):
    HERE = 0
    IN = 1
    OUT = 2


class TransportationRuleType(Enum):
    ANTIPORT = 0
    SYMPORT_IN = 1
    SYMPORT_OUT = 2


class InvalidTypeException(Exception):
    pass


class Rule(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def weight(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass


class BaseModelRule(Rule):
    def __init__(self, left_side: Dict, right_side: Dict):
        self.left_side = MultiSet(left_side)
        self.right_side = MultiSet(right_side)

    def weight(self):
        return len(self.left_side)

    def has_in_object(self):
        for (_, direction), _ in self.right_side:
            if direction == Direction.IN:
                return True
        return False

    def __str__(self):
        result = ""
        for k, v in self.left_side:
            result += k * v
        result += ' ->'
        in_objects = " IN: "
        out_objects = " OUT: "
        here_objects = " HERE: "
        for (obj, direction), v in self.right_side:
            if direction == Direction.HERE:
                here_objects += obj * v
            if direction == Direction.IN:
                in_objects += obj * v
            if direction == Direction.OUT:
                out_objects += obj * v

        right_side = in_objects + out_objects + here_objects
        result += right_side
        return result


# Majd ehhez is visszatérünk
#    def __repr__(self):
#        left_side = []
#        for k, v in self.left_side:
#            left_side.extend([k for _ in range(v)])

#        right_side = []
#        for (obj, direction), v in self.right_side:
#            if direction == Direction.HERE:
#                right_side.extend([f'{obj}_here' for _ in range(v)])
#            if direction == Direction.IN:
#                right_side.extend([f'{obj}_in' for _ in range(v)])
#            if direction == Direction.OUT:
#                right_side.extend([f'{obj}_out' for _ in range(v)])
#        return f'{left_side} -> {right_side}'

class DissolvingRule(BaseModelRule):
    def __str__(self):
        string = super().__str__()
        pos = string.index('>')
        return string[:pos+1] + '#' + string[pos+1:]

    def __init__(self, left_side, right_side):
        super().__init__(left_side, right_side)


class PriorityRule:
    avail_classes = ['BaseModelRule', 'DissolvingRule']

    def __init__(self, strong_rule, weak_rule):
        if strong_rule.__class__.__name__ in PriorityRule.avail_classes and \
                weak_rule.__class__.__name__ in PriorityRule.avail_classes:
            self.strong_rule = strong_rule
            self.weak_rule = weak_rule
        else:
            raise InvalidTypeException

    def __str__(self):
        return f'({self.strong_rule.__str__()}) > ({self.weak_rule.__str__()})'


class SymportRule(Rule):
    def __init__(self, rule_type, imported_obj=None, exported_obj=None):
        if imported_obj is None and exported_obj is None:
            raise InvalidTypeException
        self.rule_type = rule_type
        self.imported_obj = MultiSet(imported_obj) if imported_obj else None
        self.exported_obj = MultiSet(exported_obj) if exported_obj else None

    def weight(self):
        if self.rule_type == TransportationRuleType.ANTIPORT:
            return max(len(self.exported_obj), len(self.imported_obj))
        elif self.rule_type == TransportationRuleType.SYMPORT_IN:
            return len(self.imported_obj)
        else:
            return len(self.exported_obj)

    def __str__(self):
        if self.rule_type == TransportationRuleType.ANTIPORT:
            return f'IN: {self.imported_obj} OUT: {self.exported_obj}'
        if self.rule_type == TransportationRuleType.SYMPORT_IN:
            return f'IN: {self.imported_obj}'
        if self.rule_type == TransportationRuleType.SYMPORT_OUT:
            return f'OUT: {self.exported_obj}'
