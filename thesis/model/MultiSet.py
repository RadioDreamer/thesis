class ObjectNotFoundException(Exception):
    """ A class for signaling that the object being referenced is not
    contained by the multiset """
    pass


class InvalidOperationException(Exception):
    """ A class for signaling that the operation's conditions are not met by
    the multiset's state """
    pass


class NotEnoughObjectsException(Exception):
    """ A class for signaling that the multiset does not contain sufficiently
    many instances of the given object """
    pass


class MultiSet:
    """ A class for representing the objects with multiplicity in a given membrane

    Attributes
    ----------
    objects : dict
        a dict containing the objects as keys and their multiplicity as values
    """

    def __init__(self, init_objects=None):
        """
        A function used for initializing a multiset

        If the argument `init_objects` isn't passed in, the default multiset
        is empty.

        Parameters
        ----------
        init_objects : dict, optional
            The dictionary containing the objects for
            the initial state of the multiset
        """

        if init_objects:
            assert all(item > 0 for item in init_objects.values())
            self.objects = init_objects
        else:
            self.objects = {}

    def __str__(self):
        """
        A function used to display the multiset in string format

        Returns
        -------
        str
            string representation of the multiset
        """

        iter_obj = [k for k, v in self.items() for i in range(v)]
        return ''.join(iter_obj)

    def __repr__(self):
        """
        A function used to represent the multiset object

        Returns
        -------
        str
            same str as in `__str__()`
        """

        return self.objects.__repr__()

    def __getitem__(self, key):
        """
        A function used to return the multiplicity of given object

        Parameters
        ----------
        key : object
            the object whose multiplicity we want to return

        Returns
        -------
        int
            the multiplicity of the object `key` in the multiset
        """

        return self.objects[key]

    def __setitem__(self, key, new_value):
        """
        A function used to set the multiplicity of given object

        Parameters
        ----------
        key : object
            the object whose multiplicity we want to set to a new value
        new_value : int
            the new multiplicity value for the object `key`
        """

        assert new_value >= 0
        self.objects[key] = new_value

    def __eq__(self, other):
        """
        A function used to check the equality between two multisets

        Two multisets are equal if anf only if they contain exactly the same
        elements and all of them with the same multiplicity

        Parameters
        ----------
        other : MultiSet
            the other multiset we want to compare `self` to

        Returns
        -------
        bool
            True if they are equal as above mentioned, False otherwise
        """

        return self.objects.__eq__(other)

    def __len__(self):
        """
        A function that returns the length of the multiset

        The length is calculated by summing up all objects' multiplicity

        Returns
        -------
        int
            the sum of the objects' multiplicity
        """

        return sum(self.objects.values())

    def __iter__(self):
        """
        A function used for iterating through the multiset's `objects'
        dictionary

        This means that we can iterate through in the form of (object,
        multiplicity) pairs

        Returns
        -------
        dict_keyiterator
            the iterator object that can be iterated through
        """

        return iter(self.objects.items())

    def keys(self):
        """
        A function used for returning all the unique objects in the multiset

        Returns
        -------
        list
            the list object containing all the objects
        """

        return self.objects.keys()

    def items(self):
        """
        A function used for returning all the `(object, multiplicity)` pairs
        in a list

        Returns
        -------
        list
            list containing the pairs
        """

        return self.objects.items()

    def values(self):
        """
        A function used for returning all the multiplicities in the multiset

        Returns
        -------
        list
            the list object containing all the objects
        """

        return self.objects.values()

    def __contains__(self, obj):
        """
        A function used for determining whether the multiset contains the
        given object

       Returns
       -------
       bool
           True if the multiset contains `obj`, False otherwise
       """

        return obj in self.objects

    def has_subset(self, multiset):
        """
        A function used for determining whether the parameter `multiset` object
        is a subset of `self`

        A multiset `m1` is a subset of another multiset `m2` if and only if
        for every object in `m1` the other multiset  `m2` also contains that
        same object with greater or equal multiplicity

        Parameters
        ----------
        multiset : MultiSet
            the other multiset that is checked to be the subset of `self`

        Returns
        -------
        bool
            True if `multiset` is a subset, False otherwise
        """

        for obj, mul in multiset:
            if obj in self and self[obj] >= mul:
                pass
            else:
                return False
        return True

    def __iadd__(self, multiset):
        """
        A function used to add a multiset to `self`

        Adding as an operation on two multisets means that the shared
        objects' multiplicity adds up and the ones that are only present in
        of the multisets are simply added to the resulting multiset with
        their starting multiplicity

        Parameters
        ----------
        multiset : MultiSet
            the multiset we want to add to `self`

        Returns
        -------
        MultiSet
            the `self` object we added `multiset` to
        """

        for obj, mul in multiset:
            if obj in self:
                self[obj] += mul
            else:
                self[obj] = mul
        return self

    def __add__(self, multiset):
        """
        A function used to add two multisets together

        The method for adding two multisets together is described in `__iadd__`

        Parameters
        ----------
        multiset : MultiSet
            the multiset we add to `self`

        Returns
        -------
        MultiSet
            the new multiset generated by adding together the two multisets
        """

        tmp = MultiSet(self.objects)
        for obj, mul in multiset:
            if tmp[obj]:
                tmp[obj] += mul
            else:
                tmp[obj] = mul
        return tmp

    def __delitem__(self, key):
        """
        A function used to delete an object entirely from the multiset

        Parameters
        ----------
        key : object
            the object we want to delete
        """

        del self.objects[key]

    def __isub__(self, multiset):
        """
        A function used to subtract a multiset to `self`

        The subtraction operation has a condition such that the multiset we
        want to subtract has to be a subset of the other multiset. If the
        condition is met, then subtraction simply involves the subtraction of
        the multiplicities of the objects in the parameter `multiset` from
        the corresponding objects multiplicity in `self`

        Parameters
        ----------
        multiset : MultiSet
            the multiset we want to subtract from `self`

        Returns
        -------
        MultiSet
            the `self` object we subtracted `multiset` from
        """

        if self.has_subset(multiset):
            for obj, mul in multiset.items():
                self[obj] -= mul
                if self[obj] == 0:
                    del self[obj]
            return self
        else:
            raise InvalidOperationException

    def __sub__(self, multiset):
        """
       A function used to subtract two multisets together

       The method for subtracting two multisets together is described in
       `__isub__`

       Parameters
       ----------
       multiset : MultiSet
           the multiset we subtract from `self`

       Returns
       -------
       MultiSet
           the new multiset generated by subtracting `multiset` from `self`
       """

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
        """
        A function used for determining whether the multiset contains no objects

        Returns
        -------
        bool
            True if `self` is empty, False otherwise
        """

        return len(self.objects) == 0

    def add_object(self, obj, mul=1):
        """
        A function used to add an object with given multiplicity

        Parameters
        ----------
        obj : object
            the object we want to add to the multiset
        mul : int, optional
            the number of instances we want to add (default is 1)
        """

        if obj in self.objects.keys():
            self.objects[obj] = self.objects[obj] + mul
        else:
            self.objects[obj] = mul

    def remove_object(self, obj, mul=1, all=False):
        """
        A function used to remove an object with given multiplicity

        If `all` is set to true or `mul` is equal to the objects multiplicity
        in the multiset, than this functions acts as `__delitem__`

        Parameters
        ----------
        obj : object
            the object we want to remove (some or all) instances of
        mul : int, optional
            the number of instances to be removed (default is 1)
        all : bool, optional
            the flag to determine whether to remove all instances
            in the multiset (default is False)

        Raises
        -------
        NotEnoughObjectsException
            if `mul` is greater than the multiplicity of `obj` in the multiset
        ObjectNotFoundException
            if the object `obj` is not contained by the multiset
        """

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
        """
        A function used for returning the multiplicity of `obj` in the multiset

        Parameters
        ----------
        obj : object
            the object whose multiplicity we want to return

        Raises
        -------
        ObjectNotFoundException
            if the multiset does not contain `obj`

        Returns
        -------
        int
            the multiplicity of the object `obj`
        """

        if obj in self:
            return self[obj]
        else:
            raise ObjectNotFoundException

    @classmethod
    def string_to_multiset(cls, str_multiset, sep_values=[' ']):
        """
        A function used to create a multiset instance from a string

        The string can contain any of the separating values in `sep_values`

        Only works when the objects in the multiset are characters

        Parameters
        ----------
        str_multiset : str
            the string used to create the multiset
        sep_values : list
            the list containing all the separating values

        Returns
        -------
        MultiSet the multiset generated by adding all
        non-separating characters to an empty multiset
        """

        result = MultiSet()
        for c in str_multiset:
            if c in sep_values:
                continue
            else:
                result.add_object(c)
        return result
