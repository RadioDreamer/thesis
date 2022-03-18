from MultiSet import MultiSet


class Region:
    def __repr__(self):
        return "Region:" + self.objects.__repr__()

    def __init__(self, id, parent_id, objects=None,
                 rules=None):
        self.is_dissolving = False
        self.id = id
        self.parent_id = parent_id
        self.new_objects = MultiSet()
        self.objects = MultiSet(objects)
        self.rules = rules
