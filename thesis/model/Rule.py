import abc
from enum import Enum
from MultiSet import MultiSet
from typing import Dict


class Direction(Enum):
    """
    An enum class for describing the direction of an object in an evolution rule

    `HERE` means that the object stays in the region
    `IN` means that the object travels into one of the child regions
    `OUT` means that the object travels out to the region's parent
    """

    HERE = 0
    IN = 1
    OUT = 2


class TransportationRuleType(Enum):
    """
    An enum class for describing the type of the `SymportRule`

    `ANTIPORT` means that objects travel both in and out of the region
    `SYMPORT_IN` means that objects travel only into the region
    `SYMPORT_OUT` means that objects travel only out of the region
    """

    ANTIPORT = 0
    SYMPORT_IN = 1
    SYMPORT_OUT = 2


class InvalidTypeException(Exception):
    """
    A class used to represent the exception when a `PriorityRule` instance gets
    one or two incorrect type of rules as input
    """
    pass


class Rule(metaclass=abc.ABCMeta):
    """
    Abstact class describing an evolution rule in a membranesystem
    """

    @abc.abstractmethod
    def weight(self):
        """
        A function used to determine the weight of the rule
        """
        pass

    @abc.abstractmethod
    def __str__(self):
        """
        A function used to return the string representation of the rule
        """
        pass


class BaseModelRule(Rule):
    """
    A class derived from `Rule` used to describe rules that can be constructed
    in the base model of the membranesystems

    Attributes
    ----------
    left_side : MultiSet
        the required objects for the evolution rule to occur
    right_side : MultiSet
        the newly generated objects created by applying the rule to the region
    """

    def __init__(self, left_side: Dict, right_side: Dict):
        """
         A function used to initialize a `BaseModelRule` instance

        Parameters
        ----------
        left_side : Dict
            the required objects for the evolution rule to occur
        right_side : Dict
            the generated objects
        """

        self.left_side = MultiSet(left_side)
        self.right_side = MultiSet(right_side)

    def weight(self):
        """
        A function used to return the weight of the rule

        For rules in the base model, the weight is the number of objects on the
        left side

        Returns
        -------
        int
            the number of objects on the left side of the rule
        """

        return len(self.left_side)

    def has_in_object(self):
        """
        A function used to determine whether the rule has objects that travel
        inwards

        Returns
        -------
        bool
            True if at least one element travels inwards, False otherwise
        """

        for (_, direction), _ in self.right_side:
            if direction == Direction.IN:
                return True
        return False

    def __str__(self):
        """
        A function used to generate the string representation of the rule

        Returns
        -------
        str
            the string representing the rule
        """

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

class DissolvingRule(BaseModelRule):
    """
    A class used to describe a special rule in the base model

    After applying a `DissolvingRule`, the region must dissolve, leaving its
    objects and inner regions to its parent

    """

    def __str__(self):
        """
        A function used to generate the string representation of the rule

        Returns
        -------
        str
            the string representing the rule
        """

        string = super().__str__()
        pos = string.index('>')
        return string[:pos + 1] + '#' + string[pos + 1:]

    def __init__(self, left_side, right_side):
        """
         A function used to initialize a `DissolvingRule` instance

        Parameters
        ----------
        left_side : Dict
            the required objects for the evolution rule to occur
        right_side : Dict
            the generated objects
        """
        super().__init__(left_side, right_side)


class PriorityRule:
    """
    A class used to describe a notion of priority between two rules

    The 'weak' rule cannot be applied (or at least try to be applied) until
    the 'strong' rule CAN be applied
    """
    avail_classes = ['BaseModelRule', 'DissolvingRule']

    def __init__(self, strong_rule, weak_rule):
        """
        A function used to initialize a `PriorityRule` instance

        Parameters
        ----------
        strong_rule : Union[BaseModelRule,DissolvingRule]
            the stronger rule
        weak_rule : Union[BaseModelRule,DissolvingRule]
            the weaker rule

        Raises
        ------
        InvalidTypeException
            if strong_rule or weak_rule are not of given types
        """

        if strong_rule.__class__.__name__ in PriorityRule.avail_classes and \
                weak_rule.__class__.__name__ in PriorityRule.avail_classes:
            self.strong_rule = strong_rule
            self.weak_rule = weak_rule
        else:
            raise InvalidTypeException

    def __str__(self) -> str:
        """
        A function used to generate the string representation of the rule

        Returns
        -------
        str
            the string representing the rule
        """

        return f'{self.strong_rule.__str__()} > {self.weak_rule.__str__()}'


class SymportRule(Rule):
    """
    A class used to describe the rules that can be constructed in a
    SymporAntiport membrane system

    Attributes
    ----------
    rule_type : TransportationRuleType
        the type of the rule
    imported_obj : MultiSet, optional
        the objects that travel into the region (default is None)
    export_obj : MultiSet, optional
        the objects that travel out of the region (default is None)

    Raises
    ------
    InvalidTypeException
        if both `import_obj` and `export_obj` are None
    """

    def __init__(self, rule_type, imported_obj=None, exported_obj=None):
        if imported_obj is None and exported_obj is None:
            raise InvalidTypeException
        self.rule_type = rule_type
        self.imported_obj = MultiSet(imported_obj) if imported_obj else None
        self.exported_obj = MultiSet(exported_obj) if exported_obj else None

    def weight(self):
        """
        A function used to calculate the weight of the rule

        Returns
        -------
        int
            the weight of the rule
        """

        if self.rule_type == TransportationRuleType.ANTIPORT:
            return max(len(self.exported_obj), len(self.imported_obj))
        elif self.rule_type == TransportationRuleType.SYMPORT_IN:
            return len(self.imported_obj)
        else:
            return len(self.exported_obj)

    def __str__(self) -> str:
        """
        A function used to generate the string representation of the rule

        Returns
        -------
        str
            the string representing the rule
        """

        if self.rule_type == TransportationRuleType.ANTIPORT:
            return f'IN: {self.imported_obj} OUT: {self.exported_obj}'
        if self.rule_type == TransportationRuleType.SYMPORT_IN:
            return f'IN: {self.imported_obj}'
        if self.rule_type == TransportationRuleType.SYMPORT_OUT:
            return f'OUT: {self.exported_obj}'
