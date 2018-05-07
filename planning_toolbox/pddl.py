#################
## BASIC TYPES ##
#################

from copy import copy
from random import random


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


class AtomicFunctional:

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
        return AtomicFunctional(self._name, *(arg.strip_type() for arg in self._args))

    def bind(self, sigma):
        return AtomicFunctional(self._name, *(arg.bind(sigma) for arg in self._args))

    def signature(self):
        return "{}/{}".format(self._name, self.arity())

    def __eq__(self, other):
        if isinstance(other, AtomicFunctional):
            return other._name == self._name and other._args == self._args
        return False

    def __hash__(self):
        return hash((self._name, *self._args))

    def __str__(self):
        if self._args:
            return "({} {})".format(self._name,
                                    " ".join(str(arg) for arg in self._args))
        return "(" + self._name + ")"


class Predicate(AtomicFunctional):
    pass


class Function(AtomicFunctional):
    pass


class Expression:
    
    def is_atomic(self):
        raise NotImplementedError()

    def bind(self, sigma):
        raise NotImplementedError()


class AtomicExpression(Expression):

    def __init__(self, atom):
        self._atom = atom

    def atom(self):
        return self._atom

    def is_atomic(self):
        return True

    def is_symbolic(self):
        return isinstance(self._atom, AtomicFunctional)

    def bind(self, sigma):
        cpy = copy(self)
        if isinstance(self._atom, AtomicFunctional):
            cpy._atom = cpy._atom.bind(sigma)
        return cpy

    def __str__(self):
        return str(self._atom)


class ListExpression(Expression):

    def __init__(self, head, *tail):
        self._head = head
        self._tail = tail

    def head(self):
        return self._head

    def tail(self):
        return self._tail

    def is_atomic(self):
        return False

    def bind(self, sigma):
        cpy = copy(self)
        cpy._tail = tuple(e.bind(sigma) for e in cpy._tail)
        return cpy

    def __str__(self):
        if self._tail:
            return "({} {})".format(self._head,
                    " ".join(str(e) for e in self._tail))


class QuantifiedExpression(Expression):

    def __init__(self, quantifier, parameters, expression):
        if not all(isinstance(o, Object) and not o.is_ground() for o in parameters):
            raise Exception("parameters should be a list of not-ground objects")
        self._quantifier = quantifier
        self._parameters = parameters
        self._expression = expression

    def quantifier(self):
        return self._quantifier

    def parameters(self):
        return self._parameters

    def expression(self):
        return self._expression

    def is_atomic(self):
        return False

    def bind(self, sigma):
        cpy = copy(self)
        cpy._expression = cpy._expression.bind(sigma)
        return cpy

    def __str__(self):
        return "({} ({}) {})".format(self._quantifier,
                " ".join(str(p) for p in self._parameters), self._expression)


#############
## QUERIES ##
#############

class Query:

    def eval(self, state):
        return True

    def __str__(self):
        return "()"


class PredicateQuery(AtomicExpression, Query):

    def eval(self, state):
        raise NotImplementedError()


class FunctionQuery(AtomicExpression, Query):

    def eval(self, state):
        raise NotImplementedError()


class ConstantQuery(AtomicExpression, Query):

    def eval(self, state):
        # ignore state
        return self.atom()


class ArithmeticQuery(ListExpression, Query):

    def __init__(self, op, lhs, rhs):
        if op not in ("+", "-", "*", "/"):
            raise Exception("op must be one of the four available symbols (+,-,/,*)")
        super().__init__(op, lhs, rhs)

    def eval(self, state):
        lhs = self.tail()[0].eval(state)
        rhs = self.tail()[1].eval(state)
        op = self.head()
        if op == "+": return lhs + rhs
        if op == "-": return lhs - rhs
        if op == "*": return lhs*rhs
        return lhs/rhs


class ComparisonQuery(ListExpression, Query):

    def __init__(self, comp, lhs, rhs):
        if comp not in ("<", ">", "<=", "=", ">="):
            raise Exception("cmp must be one of (<,>,<=,=,>=)")
        super().__init__(comp, lhs, rhs)
        
    def eval(self, state):
        lhs = self.tail()[0].eval(state)
        rhs = self.tail()[1].eval(state)
        comp = self.head()
        if comp == "<": return lhs < rhs
        if comp == ">": return lhs > rhs
        if comp == "<=": return lhs <= rhs
        if comp == "=": return lhs == rhs
        return lhs >= rhs


class AndQuery(ListExpression, Query):

    def __init__(self, *tail):
        super().__init__("and", *tail)

    def eval(self, state):
        return all(e.eval(state) for e in self.tail())


class OrQuery(ListExpression, Query):

    def __init__(self, *tail):
        super().__init__("or", *tail)

    def eval(self, state):
        return any(e.eval(state) for e in self.tail())


class NotQuery(ListExpression, Query):

    def __init__(self, negated):
        super().__init__("not", negated)

    def eval(self, state):
        return not self.tail()[0].eval(state)


class ImplyQuery(ListExpression, Query):

    def __init__(self, lhs, rhs):
        super().__init__("imply", lhs, rhs)

    def eval(self, state):
        return not self[0].eval(state) or self[1].eval(state)


class TotalQuery(QuantifiedExpression, Query):

    def __init__(self, parameters, exp):
        super().__init__("forall", parameters, exp)

    def eval(self, state):
        raise NotImplementedError()


class ExistentialQuery(QuantifiedExpression, Query):

    def __init__(self, parameters, exp):
        super().__init__("exists", parameters, exp)

    def eval(self, state):
        raise NotImplementedError()


#############
## EFFECTS ##
#############

class Effect:

    def apply(self, state, out=None):
        if out is None: out = copy(state)
        return out

    def __str__(self):
        return "()"


class AddEffect(AtomicExpression, Effect):

    def __init__(self, predicate):
        super().__init__(predicate)

    def apply(self, state, out=None):
        return super().apply(state, out)


class DeleteEffect(ListExpression, Effect):

    def __init__(self, predicate):
        super().__init__("not", predicate)

    def apply(self, state, out=None):
        return super().apply(state, out)


class AndEffect(ListExpression, Effect):

    def __init__(self, *tail):
        super().__init__("and", *tail)

    def apply(self, state, out=None):
        out = super().apply(state, out)
        for effect in self.tail():
            out = effect.apply(state, out)
        return out


class TotalEffect(QuantifiedExpression, Effect):

    def __init__(self, parameters, effect):
        super().__init__("forall", parameters, effect)

    def apply(self, state, out=None):
        return super().apply(state, out)


class ConditionalEffect(ListExpression, Effect):

    def __init__(self, lhs, rhs):
        super().__init__("when", lhs, rhs)

    def apply(self, state, out=None):
        out = super().apply(state, out)
        lhs = self.tail()[0].eval(state)
        if lhs:
            out = rhs.apply(state, out)
        return out


class AssignmentEffect(ListExpression, Effect):

    def __init__(self, assign, lhs, rhs):
        if assign not in ("assign", "increase", "decrease", "scale-up",
                          "scale-down"):
            raise Exception("assign operator must be one of (assign, "
                            "increase, decrease, scale-up, scale-down)")
        super().__init__(assign, lhs, rhs)

    def apply(self, state, out=None):
        return super().apply(state, out)


class ProbabilisticEffect(ListExpression, Effect):

    def __init__(self, *tail):
        total_prob = 0
        for e in tail[::2]:
            total_prob += e
        if total_prob > 1+1e-6:
            raise Exception("Probability greater than 1")
        super().__init__("probabilistic", *tail)

    def __len__(self):
        return len(self.tail()) // 2

    def __getitem__(self, idx):
        return self.tail()[idx*2:(idx+1)*2]

    def __iter__(self):
        for idx in range(len(self)):
            yield self[idx]

    def apply(self, state, out=None):
        out = super().apply(state, out)
        r = random()
        acc = 0
        for p, effect in self:
            acc += p
            if r < p:
                out = effect.apply(state, out)
                break
        return out


####################
## DOMAIN OBJECTS ##
####################

class Action:

    def __init__(self, name, parameters, precondition, effect):
        self._name = name
        self._parameters = parameters
        self._precondition = precondition
        self._effect = effect

    def name(self):
        return self._name

    def parameters(self):
        return self._parameters

    def precondition(self):
        return self._precondition

    def effect(self):
        return self._effect

    def is_applicable(self, state):
        raise NotImplementedError()

    def apply(self, state):
        raise NotImplementedError()

    def __str__(self):
        return "(:action {}\n:parameters ({})\n:precondition {}\n:effect {})".format(
                self._name, " ".join(map(str, self._parameters)),
                self._precondition, self._effect)


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




