

class Object:

    def __init__(self, name, type_=None):
        self._name = name
        self._type = type_

    def name(self):
        return self._name

    def type(self):
        return self._type

    def is_ground(self):
        return self._name[0] != "?"

    def strip_type(self):
        return Object(self._name)

    def bind(self, sigma):
        try:
            return Object(sigma[self._name], self._type)
        except KeyError:
            return self

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        if isinstance(other, Object):
            return other._name == self._name
        if isinstance(other, str):
            return other == self._name
        return False

    def __str__(self):
        if self._type is not None and not self.is_ground():
            return self._name + " - " + self._type
        return self._name


class Predicate:

    def __init__(self, name, *args):
        self._name = name
        self._args = args

    def name(self):
        return self._name

    def args(self):
        return self._args

    def arity(self):
        return len(self._args)

    def is_ground(self):
        return all(arg.is_ground() for arg in self._args)

    def strip_types(self):
        return Predicate(self._name, *(arg.strip_type() for arg in self._args))

    def bind(self, sigma):
        return Predicate(self._name, *(arg.bind(sigma) for arg in self._args))

    def signature(self):
        return "{}/{}".format(self._name, self.arity())

    def __eq__(self, other):
        if isinstance(other, Object):
            return other._name == self._name and other._args == self._args
        if isinstance(other, (list, tuple)):
            return other[0] == self._name and other[1:] == self._args
        return False

    def __hash__(self):
        return hash((self._name, *self._args))

    def __str__(self):
        if self._args:
            return "({} {})".format(self._name,
                                    " ".join(str(arg) for arg in self._args))
        return "(" + self._name + ")"

