import abc
from enum import Enum
from MultiSet import MultiSet


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


class BaseModelRule(Rule):
    def __init__(self, left_side, right_side):
        self.left_side = MultiSet(left_side)
        self.right_side = MultiSet(right_side)

    def weight(self):
        return len(self.left_side)


class DissolvingRule(BaseModelRule):
    def __init__(self, left_side, right_side):
        super().__init__(left_side, right_side)


class PriorityRule():
    avail_classes = ['BaseModelRule', 'DissolvingRule']

    def __init__(self, strong_rule, weak_rule):
        if strong_rule.__class__.__name__ in PriorityRule.avail_classes and \
                weak_rule.__class__.__name__ in PriorityRule.avail_classes:
            self.strong_rule = strong_rule
            self.weak_rule = weak_rule
        else:
            raise InvalidTypeException


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
