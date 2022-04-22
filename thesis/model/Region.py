from MultiSet import MultiSet
from PySide6.QtCore import QObject, Signal


class RegionSignal(QObject):
    """
    A class for representing the signals that the region emits when either
    its objects or rules change

    Attributes
    ----------
    obj_changed : Signal
        a signal for communicating to the model that the regions' objects have
        changed
    rules_changed : Signal
        a signal for communicating to the model that the regions' rules have
        changed
    """

    obj_changed = Signal(int, str)
    rules_changed = Signal(int, str)


class Region(QObject):
    """
    A class for representing a region in a membranesystem

    Attributes
    ----------
    is_dissolving : bool
        a flag used to indicate that the region is being dissolved
    id : int
        the identifier of the region
    new_objects : MultiSet
        contains the newly generated objects in a simulation step
    _objects : MultiSet
        contains the currently present objects in a simulation step
    _rules : list
        contains the evolution rules for the region
    signal : RegionSignal
        used for signaling changes in state to the model
    """

    def __init__(self, id, objects=None,
                 rules=None):
        """
        A function used to initialize a region

        Parameters
        ----------
        id : int
            the unique identifier of the region
        objects : MultiSet
            the objects currently contained by the region
        rules : list
            the list of rules that can act in the region
        """

        self.is_dissolving = False
        self.id = id
        self.new_objects = MultiSet()
        self._objects = MultiSet(objects)
        self._rules = [] if rules is None else rules
        self.signal = RegionSignal()

    @property
    def rules(self):
        """
        A function used to get the region's rules

        Returns
        -------
        list
            the list of the rules
        """
        return self._rules

    @rules.setter
    def rules(self, value):
        """
        A function used to modify the list of rules

        Emits `rules_changed`

        Parameters
        ----------
        value : list
            the list containing the rules we override the older ones with
        """
        self._rules = value
        result = self.get_rule_string()
        self.signal.rules_changed.emit(self.id, result)

    @property
    def objects(self):
        """
        A function used to get the region's objects

        Returns
        -------
        MultiSet
            the currently contained objects
        """
        return self._objects

    @objects.setter
    def objects(self, value):
        """
        A function used to modify the region's objects

        Emits `obj_changed`

        Parameters
        ----------
        value : MultiSet
            the multiset containing the new state of `objects`
        """

        self.signal.obj_changed.emit(self.id, str(value))
        self._objects = value

    def __repr__(self):
        """
        A function used to generate the instance representation
        """

        return "Region:" + self.objects.__repr__()

    def get_rule_string(self):
        """
        A function used to generate a string containing all the rules in the
        region

        Returns
        -------
        str
            the string containing all the region's rules separated by '\n'
        """

        rule_str = [str(r) for r in self._rules]
        return '\n'.join(rule_str)

    def add_rule(self, rule):
        self.rules.append(rule)
        result = self.get_rule_string()
        self.signal.rules_changed.emit(self.id, result)
