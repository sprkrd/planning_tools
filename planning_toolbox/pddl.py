#################
## BASIC TYPES ##
#################

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
        return False

    def __str__(self):
        if self._type is not None and not self.is_ground():
            return self._name + " - " + self._type
        return self._name


class Predicate:

    def __init__(self, name, *args):
        self._name = name
        self._args = tuple(to_object(arg) for arg in args)

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
        if isinstance(other, Predicate):
            return other._name == self._name and other._args == self._args
        return False

    def __hash__(self):
        return hash((self._name, *self._args))

    def __str__(self):
        if self._args:
            return "({} {})".format(self._name,
                                    " ".join(str(arg) for arg in self._args))
        return "(" + self._name + ")"


class Function(Predicate):
    pass


class ExpressionBase:

    def __init__(self, root, *children):
        self._root = root
        self._children = children
        
    def root(self):
        return self._root

    def is_atomic(self):
        raise NotImplementedError()

    def __len__(self):
        return len(self._children)

    def __iter__(self):
        return self._children.__iter__()

    def __getitem__(self, idx):
        return self._children[idx]

    def __str__(self):
        if self.is_atomic():
            return str(self._root)
        if self._children:
            return "({} {})".format(self._root, " ".join(
                str(child) for child in self._children))
        return "({})".format(self._root)


#############
## QUERIES ##
#############

class Query(ExpressionBase):

    def eval(self, state):
        raise NotImplementedError()


class Number(Query):

    def __init__(self, number):
        super().__init__(number)
        assert isinstance(number, (float, int))

    def eval(self, state):
        # ignore state
        return self.root()

    def is_atomic(self):
        return True


class AtomicQuery(Query):

    def __init__(self, predicate):
        super().__init__(predicate)
        assert isinstance(predicate, Predicate)

    def eval(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return True


class FunctionQuery(Query):

    def __init__(self, function):
        super().__init__(function)
        assert isinstance(function, Function)

    def eval(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return True


class ArithmeticQuery(Query):

    def __init__(self, op, lhs, rhs):
        super().__init__(op, lhs, rhs)
        assert op in ("+", "-", "*", "/")

    def eval(self, state):
        lhs = self[0].eval(state)
        rhs = self[1].eval(state)
        op = self.root()
        if op == "+": return lhs + rhs
        if op == "-": return lhs - rhs
        if op == "*": return lhs*rhs
        return lhs/rhs

    def is_atomic(self):
        return False


class ComparisonQuery(Query):

    def __init__(self, comparison, lhs, rhs):
        super().__init__(comparison, lhs, rhs)
        assert comparison in ("<", ">", "<=", "=", ">=")
        
    def eval(self, state):
        lhs = self[0].eval(state)
        rhs = self[1].eval(state)
        comp = self.root()
        if comp == "<": return lhs < rhs
        if comp == ">": return lhs > rhs
        if comp == "<=": return lhs <= rhs
        if comp == "=": return lhs == rhs
        return lhs >= rhs

    def is_atomic(self):
        return False


class AndQuery(Query):

    def __init__(self, *children):
        super().__init__("and", *children)

    def eval(self, state):
        return all(child.eval(state) for child in self)

    def is_atomic(self):
        return False


class OrQuery(Query):

    def __init__(self, *children):
        super().__init__("or", *children)

    def eval(self, state):
        return any(child.eval(state) for child in self)

    def is_atomic(self):
        return False


class NotQuery(Query):

    def __init__(self, negated):
        super().__init__("not", negated)

    def eval(self, state):
        return not self[0].eval(state)

    def is_atomic(self):
        return False


class ImplyQuery(Query):

    def __init__(self, lhs, rhs):
        super().__init__("imply", lhs, rhs)

    def eval(self, state):
        return not self[0].eval(state) or self[1].eval(state)

    def is_atomic(self):
        return False


class TotalQuery(Query):

    def __init__(self, variables, exp):
        super().__init__("forall", exp)
        assert all(isinstance(obj, Object) and not obj.is_ground()
                   for obj in variables)
        self._variables = variables

    def eval(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return False

    def __str__(self):
        return "(forall ({}) {})".format(
                " ".join(str(obj) for obj in self._variables), self[0])


class ExistentialQuery(Query):

    def __init__(self, variables, exp):
        super().__init__("exists", exp)
        assert all(not obj.is_ground() for obj in variables)
        self._variables = variables

    def eval(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return False

    def __str__(self):
        return "(exists ({}) {})".format(
                " ".join(str(obj) for obj in self._variables), self[0])


#############
## EFFECTS ##
#############

class Effect(ExpressionBase):

    def apply(self, state):
        raise NotImplementedError()


class AtomicEffect(Effect):

    def __init__(self, predicate):
        super().__init__(predicate)
        assert isinstance(predicate, Predicate)

    def apply(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return True


class DeleteEffect(Effect):

    def __init__(self, predicate):
        super().__init__("not", predicate)
        assert isinstance(predicate, Predicate)

    def apply(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return False


class AndEffect(Effect):

    def __init__(self, *children):
        super().__init__("and", *children)
        assert all(isinstance(child, Effect) for child in children)

    def apply(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return False


class TotalEffect(Effect):

    def __init__(self, variables, effect):
        super().__init__("forall", effect)
        assert all(isinstance(obj, Object) and not obj.is_ground()
                   for obj in variables)
        self._variables = variables

    def apply(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return False

    def __str__(self):
        return "(forall ({}) {})".format(
                " ".join(str(obj) for obj in self._variables), self[0])


class ConditionalEffect(Effect):

    def __init__(self, lhs, rhs):
        super().__init__("when", lhs, rhs)
        assert isinstance(lhs, Query)
        assert isinstance(rhs, Effect)

    def apply(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return False


class AssignmentEffect(Effect):

    def __init__(self, assign, lhs, rhs):
        super().__init__(assign, lhs, rhs)
        assert isinstance(lhs, Function)
        assert isinstance(rhs, (ArithmeticQuery, FunctionQuery, Number))


    def apply(self, state):
        raise NotImplementedError()

    def is_atomic(self):
        return False


####################
## DOMAIN OBJECTS ##
####################


class Action:

    def __init__(self, parameters):
        assert all(isinstance(param, Object) for param in parameters)
        self._parameters = parameters

    def parameters(self):
        return self._parameters

    def is_applicable(self, state):
        raise NotImplementedError()

    def apply(self, state):
        raise NotImplementedError()


class RichAction(Action):


    pass


class StripsAction:
    pass


####################
## HELPER METHODS ##
####################

def to_object(obj):
    if isinstance(obj, Object):
        return obj
    if isinstance(obj, (tuple, list)):
        name, type_ = obj
        return Object(name, type_)
    else:
        return Object(obj)




