from MultiSet import MultiSet
from PySide6.QtCore import QObject, Signal


class RegionSignal(QObject):
    obj_changed = Signal(int, str)
    rules_changed = Signal(int, list)


class Region(QObject):
    def __repr__(self):
        return "Region:" + self.objects.__repr__()

    def __init__(self, id, objects=None,
                 rules=None):
        self.is_dissolving = False
        self.id = id
        self.new_objects = MultiSet()
        self._objects = MultiSet(objects)
        self._rules = [] if rules is None else rules
        self.signal = RegionSignal()

    def get_rule_string(self):
        rule_str = [str(r) for r in self.rules]
        return '\n'.join(rule_str)

    @property
    def rules(self):
        return self._rules

    @rules.setter
    def rules(self,value):
        self._objects = value
        result = self.get_rule_string()
        self.signal.rules_changed.emit(self.id, result)

    @property
    def objects(self):
        return self._objects

    @objects.setter
    def objects(self,value):
        self.signal.obj_changed.emit(self.id, str(value))
        self._objects = value

