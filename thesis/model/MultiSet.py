class ObjectNotFoundException(Exception):
    pass


class InvalidOperationException(Exception):
    pass


class NotEnoughObjectsException(Exception):
    pass


class MultiSet:
    """ A class for representing the objects in a given membrane

    ...


    Attributes
    ----------
    objects : dict
        a dict containing the objects as keys and their multiplicity as values

    Methods
    -------
    has_subset(multiset)
        checks if the multiset contains the given multiset

    is_empty(multiset)
        checks if the multiset is empty

    multiplicity(obj)
        returns the multiplicity of the given object
    """

    def __init__(self, init_objects=None):
        if init_objects:
            assert all(item > 0 for item in init_objects.values())
            self.objects = init_objects
        else:
            self.objects = {}

    def __str__(self):
        iter_obj = [k for k, v in self.items() for i in range(v)]
        return ''.join(iter_obj)

    def __repr__(self):
        return self.objects.__repr__()

    def __getitem__(self, key):
        return self.objects[key]

    def __setitem__(self, key, new_value):
        assert new_value >= 0
        self.objects[key] = new_value

    def __eq__(self, other):
        return self.objects.__eq__(other)

    def __len__(self):
        return sum(self.objects.values())

    def __iter__(self):
        return iter(self.objects.items())

    def keys(self):
        return self.objects.keys()

    def items(self):
        return self.objects.items()

    def values(self):
        return self.objects.values()

    def __contains__(self, obj):
        return obj in self.objects

    def has_subset(self, multiset):
        for obj, mul in multiset:
            if obj in self and self[obj] >= mul:
                pass
            else:
                return False
        return True

    def __iadd__(self, multiset):
        for obj, mul in multiset:
            if obj in self:
                self[obj] += mul
            else:
                self[obj] = mul
        return self

    def __add__(self, multiset):
        tmp = MultiSet(self.objects)
        for obj, mul in multiset:
            if tmp[obj]:
                tmp[obj] += mul
            else:
                tmp[obj] = mul
        return tmp

    def __delitem__(self, key):
        del self.objects[key]

    def __isub__(self, multiset):
        if self.has_subset(multiset):
            for obj, mul in multiset.items():
                self[obj] -= mul
                if self[obj] == 0:
                    del self[obj]
            return self
        else:
            raise InvalidOperationException

    def __sub__(self, multiset):
        tmp = MultiSet(self.objects)
        if self.has_subset(multiset):
            for obj, mul in multiset:
                tmp[obj] -= mul
                if tmp[obj] == 0:
                    del tmp[obj]
            return tmp
        else:
            raise InvalidOperationException

    def is_empty(self):
        return len(self.objects) == 0

    def add_object(self, obj, mul=1):
        if obj in self.objects.keys():
            self.objects[obj] = self.objects[obj] + mul
        else:
            self.objects[obj] = mul

    def remove_object(self, obj, mul=1, all=False):
        if obj in self.objects.keys():
            if all or mul == self.objects[obj]:
                del self.objects[obj]
            elif mul < self.objects[obj]:
                self.objects[obj] = self.objects[obj] - mul
            else:
                raise NotEnoughObjectsException
        else:
            raise ObjectNotFoundException

    def multiplicity(self, obj):
        if obj in self:
            return self[obj]
        else:
            raise ObjectNotFoundException

    @classmethod
    def string_to_multiset(cls, str_multiset, sep_values=[' ']):
        result = MultiSet()
        for c in str_multiset:
            if c in sep_values:
                continue
            else:
                result.add_object(c)
        return result
