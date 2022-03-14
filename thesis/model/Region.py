from MultiSet import MultiSet


class Region:
    def __init__(self, id, parent_id, is_dissolving=False, objects=None,
                 rules=None):
        self.is_dissolving = is_dissolving
        self.id = id
        self.parent_id = parent_id
        self.new_objects = MultiSet()
        self.objects = MultiSet(objects)
        self.rules = rules

