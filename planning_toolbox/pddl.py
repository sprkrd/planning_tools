#################
## BASIC TYPES ##
#################

from copy import copy
from random import random


class Expression:
    
    def is_ground(self):
        raise NotImplementedError()

    def bind(self, sigma):
        raise NotImplementedError()


class Object(Expression):

    def __init__(self, name, type_=None):
        self.name = name
        self.type = type_

    def is_ground(self):
        return self.name[0] != "?"

    def strip_type(self):
        return Object(self.name)

    def bind(self, sigma):
        try:
            return Object(sigma[self.name], self.type)
        except KeyError:
            return self

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other.name == self.name 

    def __str__(self):
        if self.type is not None and not self.is_ground():
            return self.name + " - " + self.type
        return self.name


class ObjectList(Expression):

    def __init__(self, *objects):
        self.objects = tuple(to_object(obj) for obj in objects)

    def bind(self, sigma):
        return ObjectList(obj.bind(sigma) for obj in self.objects)

    def strip_types(self):
        return ObjectList(Object(obj.name) for obj in self.objects)

    def __iter__(self):
        return self.objects.__iter__()

    def __getitem__(self, idx):
        return self.objects[idx]

    def __len__(self):
        return len(self.objects)

    def __bool__(self):
        return bool(self.objects)

    def __eq__(self, other):
        return self.objects == other.objects

    def __hash__(self):
        return hash(self.objects)

    def __str__(self):
        ret = "("
        first = True
        for obj, next_obj in zip(self.objects, (*self.objects[1:], None)):
            if not first: ret += " "
            ret += obj.name
            same_type = next_obj is not None and next_obj.type == obj.type
            if obj.type and not obj.is_ground() and not same_type:
                ret += " - " + obj.type
            first = False
        ret += ")"
        return ret


class Functional(Expression):

    def __init__(self, name, *args):
        self.name = name
        if len(args) == 1 and isinstance(args[0], ObjectList):
            self.arguments = args[0]
        else:
            self.arguments = ObjectList(*args)

    def arity(self):
        return len(self.arguments)

    def is_ground(self):
        return self.arguments.is_ground()

    def strip_types(self):
        return Functional(self.name, self.arguments.strip_types())

    def bind(self, sigma):
        return Functional(self.name, self.arguments.bind(sigma))

    def signature(self):
        return "{}/{}".format(self.name, self.arity())

    def __eq__(self, other):
        return other.name == self.name and other.arguments == self.arguments

    def __hash__(self):
        return hash((self.name,*self.arguments))

    def __str__(self):
        if self.arguments:
            return "(" + self.name + " " + str(self.arguments)[1:]
        return "(" + self.name + ")"


class Predicate(Functional):
    pass


class Function(Functional):
    
    def __init__(self, name, *args, type_=None):
        super().__init__(name, *args)
        self.type = type_

    def __str__(self):
        s = super().__str__()
        if self.type: s += " - " + self.type
        return s


class Constant(Expression):

    def __init__(self, constant):
        self.constant = constant

    def is_ground(self):
        return True

    def bind(self, sigma):
        return self

    def __str__(self):
        return str(self.constant)


class Compound(Expression):

    def __init__(self, head, *tail):
        self.head = head
        self.tail = tail

    def is_ground(self):
        return all(a.is_ground() for a in self.tail)

    def bind(self, sigma):
        return Compound(head, *(t.bind(sigma) for t in self.tail))

    def __str__(self):
        if self.tail:
            return "({} {})".format(self.head, " ".join(str(e) for e in self.tail))
        return "(" + self.head + ")"


#############
## QUERIES ##
#############

class Query:

    def eval(self, state):
        raise NotImplementedError()


class EmptyQuery(Query):
    
    def eval(self, state):
        return True

    def __str__(self):
        return "()"


class PredicateQuery(Query):

    def __init__(self, predicate):
        self.predicate = predicate

    def eval(self, state):
        raise NotImplementedError()

    def __str__(self):
        return str(self.predicate)


class FunctionQuery(Query):

    def __init__(self, function):
        self.function = function

    def eval(self, state):
        raise NotImplementedError()

    def __str__(self):
        return str(self.function)


class ConstantQuery(Query):

    def __init__(self, constant):
        self.constant = constant

    def eval(self, state):
        return self.constant

    def __str__(self):
        return str(self.constant)


class ArithmeticQuery(Query):

    def __init__(self, operator, lhs, rhs):
        assert operator in ("+","-","*","/")
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def eval(self, state):
        lhs = self.lhs.eval(state)
        rhs = self.rhs.eval(state)
        operator = self.operator
        if operator == "+": return lhs + rhs
        if operator == "-": return lhs - rhs
        if operator == "*": return lhs*rhs
        return lhs/rhs

    def __str__(self):
        return "({} {} {})".format(self.operator, self.lhs, self.rhs)


class ComparisonQuery(Query):

    def __init__(self, comparison, lhs, rhs):
        assert comparison in ("<", ">", "<=", "=", ">=")
        self.comparison = comparison
        self.lhs = lhs
        self.rhs = rhs
        
    def eval(self, state):
        lhs = self.lhs.eval(state)
        rhs = self.rhs.eval(state)
        comparison = self.head()
        if comparison == "<": return lhs < rhs
        if comparison == ">": return lhs > rhs
        if comparison == "<=": return lhs <= rhs
        if comparison == "=": return lhs == rhs
        return lhs >= rhs

    def __str__(self):
        return "({} {} {})".format(self.comparison, self.lhs, self.rhs)


class AndQuery(Query):

    def __init__(self, *args):
        self.args = args

    def eval(self, state):
        return all(a.eval(state) for a in self.args)

    def __str__(self):
        if self.args:
            return "(and {})".format(" ".join(str(a) for a in self.args))
        return "(and)"


class OrQuery(Query):

    def __init__(self, *args):
        self.args = args

    def eval(self, state):
        return any(a.eval(state) for a in self.args)

    def __str__(self):
        if self.args:
            return "(or {})".format(" ".join(str(a) for a in self.args))
        return "(or)"


# class NotQuery(ListExpression, Query):

    # def __init__(self, negated):
        # super().__init__("not", negated)

    # def eval(self, state):
        # return not self.tail()[0].eval(state)


# class ImplyQuery(ListExpression, Query):

    # def __init__(self, lhs, rhs):
        # super().__init__("imply", lhs, rhs)

    # def eval(self, state):
        # return not self[0].eval(state) or self[1].eval(state)


# class TotalQuery(QuantifiedExpression, Query):

    # def __init__(self, parameters, exp):
        # super().__init__("forall", parameters, exp)

    # def eval(self, state):
        # raise NotImplementedError()


# class ExistentialQuery(QuantifiedExpression, Query):

    # def __init__(self, parameters, exp):
        # super().__init__("exists", parameters, exp)

    # def eval(self, state):
        # raise NotImplementedError()


# #############
# ## EFFECTS ##
# #############

# class Effect:

    # def apply(self, state, out=None):
        # if out is None: out = copy(state)
        # return out

    # def __str__(self):
        # return "()"


# class AddEffect(AtomicExpression, Effect):

    # def __init__(self, predicate):
        # super().__init__(predicate)

    # def apply(self, state, out=None):
        # return super().apply(state, out)


# class DeleteEffect(ListExpression, Effect):

    # def __init__(self, predicate):
        # super().__init__("not", predicate)

    # def apply(self, state, out=None):
        # return super().apply(state, out)


# class AndEffect(ListExpression, Effect):

    # def __init__(self, *tail):
        # super().__init__("and", *tail)

    # def apply(self, state, out=None):
        # out = super().apply(state, out)
        # for effect in self.tail():
            # out = effect.apply(state, out)
        # return out


# class TotalEffect(QuantifiedExpression, Effect):

    # def __init__(self, parameters, effect):
        # super().__init__("forall", parameters, effect)

    # def apply(self, state, out=None):
        # return super().apply(state, out)


# class ConditionalEffect(ListExpression, Effect):

    # def __init__(self, lhs, rhs):
        # super().__init__("when", lhs, rhs)

    # def apply(self, state, out=None):
        # out = super().apply(state, out)
        # lhs = self.tail()[0].eval(state)
        # if lhs:
            # out = rhs.apply(state, out)
        # return out


# class AssignmentEffect(ListExpression, Effect):

    # def __init__(self, assign, lhs, rhs):
        # if assign not in ("assign", "increase", "decrease", "scale-up",
                          # "scale-down"):
            # raise Exception("assign operator must be one of (assign, "
                            # "increase, decrease, scale-up, scale-down)")
        # super().__init__(assign, lhs, rhs)

    # def apply(self, state, out=None):
        # return super().apply(state, out)


# class ProbabilisticEffect(ListExpression, Effect):

    # def __init__(self, *tail):
        # total_prob = 0
        # for e in tail[::2]:
            # total_prob += e
        # if total_prob > 1+1e-6:
            # raise Exception("Probability greater than 1")
        # super().__init__("probabilistic", *tail)

    # def __len__(self):
        # return len(self.tail()) // 2

    # def __getitem__(self, idx):
        # return self.tail()[idx*2:(idx+1)*2]

    # def __iter__(self):
        # for idx in range(len(self)):
            # yield self[idx]

    # def apply(self, state, out=None):
        # out = super().apply(state, out)
        # r = random()
        # acc = 0
        # for p, effect in self:
            # acc += p
            # if r < p:
                # out = effect.apply(state, out)
                # break
        # return out


# ####################
# ## DOMAIN OBJECTS ##
# ####################

# class Action:

    # def __init__(self, name, parameters, precondition, effect):
        # self._name = name
        # self._parameters = parameters
        # self._precondition = precondition
        # self._effect = effect

    # def name(self):
        # return self._name

    # def parameters(self):
        # return self._parameters

    # def precondition(self):
        # return self._precondition

    # def effect(self):
        # return self._effect

    # def is_applicable(self, state):
        # raise NotImplementedError()

    # def apply(self, state):
        # raise NotImplementedError()

    # def __str__(self):
        # return "(:action {}\n:parameters ({})\n:precondition {}\n:effect {})".format(
                # self._name, " ".join(map(str, self._parameters)),
                # self._precondition, self._effect)


# class Domain:

    # def __init__(self, name, requirements=None, type_hierarchy=None,
            # predicates=None, functions=None, actions=None):
        # self.name = name
        # self.requirements = requirements
        # self.type_hierarchy = type_hierarchy
        # self.predicates = predicates
        # self.functions = functions 
        # self.actions = actions

    # def __str__(self):
        # ret = "(define (domain " + self.name + ")\n"
        # if self.requirements:
            # ret += "(:requirements " + " ".join(self.requirements) + ")\n"
        # if self.type_hierarchy:
            # ret += "(:types "
            # ret += " ".join(t + ((" - " + p) if p else "") for t,p in self.type_hierarchy.items())
            # ret += ")\n"
        # if self.predicates:
            # ret += "(:predicates " + " ".join(str(p) for p in self.predicates) + ")\n"
        # if self.functions:
            # ret += "(:functions " + " ".join(str(f) + ((" - " + t) if t else "") for f,t in self.functions.items()) + ")\n"
        # ret += "\n\n".join(map(str, self.actions))
        # ret += "\n)"
        # return ret


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




