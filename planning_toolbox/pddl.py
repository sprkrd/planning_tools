#################
## BASIC TYPES ##
#################

from copy import copy
from random import random


class Object:

    def __init__(self, name, type_=None):
        self.name = name
        self.type = type_

    def is_ground(self):
        return self.name[0] != "?"

    def bind(self, sigma):
        try:
            return Object(sigma[self.name], self.type)
        except KeyError:
            return self

    def strip_type(self):
        return Object(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other.name == self.name 

    def __str__(self):
        if self.type is not None and not self.is_ground():
            return self.name + " - " + self.type
        return self.name


class ObjectList:

    def __init__(self, *objects):
        self.objects = tuple(to_object(obj) for obj in objects)

    def bind(self, sigma):
        return ObjectList(*(obj.bind(sigma) for obj in self.objects))

    def is_ground(self):
        return all(o.is_ground for o in self.objects)

    def strip_types(self):
        return ObjectList(*(Object(obj.name) for obj in self.objects))

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
        ret = ""
        first = True
        for obj, next_obj in zip(self.objects, (*self.objects[1:], None)):
            if not first: ret += " "
            ret += obj.name
            same_type = next_obj is not None and next_obj.type == obj.type
            if obj.type and not obj.is_ground() and not same_type:
                ret += " - " + obj.type
            first = False
        return ret


class Functional:

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
            return "(" + self.name + " " + str(self.arguments) + ")"
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


#############
## QUERIES ##
#############

class Query:

    def eval(self, state):
        raise NotImplementedError()

    def bind(self, sigma):
        raise NotImplementedError()


class EmptyQuery(Query):
    
    def eval(self, state):
        return True

    def bind(self, sigma):
        return self

    def __str__(self):
        return "()"


class PredicateQuery(Query):

    def __init__(self, predicate):
        self.predicate = predicate

    def eval(self, state):
        raise NotImplementedError()

    def bind(self, sigma):
        return PredicateQuery(self.predicate.bind(sigma))

    def __str__(self):
        return str(self.predicate)


class FunctionQuery(Query):

    def __init__(self, function):
        self.function = function

    def eval(self, state):
        raise NotImplementedError()

    def bind(self, sigma):
        return FunctionQuery(self.function.bind(sigma))

    def __str__(self):
        return str(self.function)


class Constant(Query):

    def __init__(self, constant):
        self.constant = constant

    def eval(self, state):
        return self.constant

    def bind(self, sigma):
        return self

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

    def bind(self, sigma):
        return ArithmeticQuery(self.operator, self.lhs.bind(sigma),
                self.rhs.bind(sigma))

    def __str__(self):
        return lisp_list_to_str(self.operator, self.lhs, self.rhs)


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

    def bind(self, sigma):
        return ComparisonQuery(self.comparison, self.lhs.bind(sigma),
                self.rhs.bind(sigma))

    def __str__(self):
        return lisp_list_to_str(self.comparison, self.lhs, self.rhs)


class AndQuery(Query):

    def __init__(self, *queries):
        self.queries = queries

    def eval(self, state):
        return all(a.eval(state) for a in self.queries)

    def bind(self, sigma):
        return AndQuery(*(a.bind(sigma) for a in self.queries))

    def __str__(self):
        return lisp_list_to_str("and", *self.queries)


class OrQuery(Query):

    def __init__(self, *queries):
        self.args = queries

    def eval(self, state):
        return any(a.eval(state) for a in self.queries)

    def bind(self, sigma):
        return OrQuery(*(a.bind(sigma) for a in self.queries))

    def __str__(self):
        return lisp_list_to_str("or", *self.queries)


class NotQuery(Query):

    def __init__(self, negated):
        self.negated = negated

    def eval(self, state):
        return not self.negated.eval(state)

    def bind(self, sigma):
        return NotQuery(self.negated.bind(sigma))

    def __str__(self):
        return lisp_list_to_str("not", self.negated)


class ImplyQuery(Query):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def eval(self, state):
        return not self.lhs.eval(state) or self.rhs.eval(state)

    def bind(self, sigma):
        return ImplyQuery(self.lhs.bind(sigma), self.rhs.bind(sigma))

    def __str__(self):
        return lisp_list_to_str("imply", self.lhs, self.rhs)


class ForallQuery(Query):

    def __init__(self, parameters, query):
        self.parameters = parameters
        self.query = query

    def eval(self, state):
        raise NotImplementedError()

    def bind(self, sigma):
        return ForallQuery(self.parameters.bind(sigma), self.query.bind(sigma))

    def __str__(self):
        return "(forall ({}) {})".format(self.parameters, self.query)


class ExistsQuery(Query):

    def __init__(self, parameters, query):
        self.parameters = parameters
        self.query = query

    def eval(self, state):
        raise NotImplementedError()

    def bind(self, sigma):
        return ExistsQuery(self.parameters.bind(sigma), self.query.bind(sigma))

    def __str__(self):
        return "(exists ({}) {})".format(self.parameters, self.query)


#############
## EFFECTS ##
#############

class Effect:

    def apply(self, state, out=None):
        raise NotImplementedError()

    def bind(self, sigma):
        raise NotImplementedError()

    def modified_predicates(self):
        raise NotImplementedError()

    def modified_functions(self):
        raise NotImplementedError()


class EmptyEffect(Effect):

    def apply(self, state, out=None):
        return state.copy() if out is None else out

    def bind(self, sigma):
        return self

    def modified_predicates(self):
        return set()

    def modified_functions(self):
        return set()

    def __str__(self):
        return "()"


class AddEffect(Effect):

    def __init__(self, add):
        self.add = add

    def apply(self, state, out=None):
        raise NotImplementedError()

    def bind(self, sigma):
        return AddEffect(self.add.bind(sigma))

    def modified_predicates(self):
        return set([self.add.name])

    def modified_functions(self):
        return set()

    def __str__(self):
        return str(self.add)


class DeleteEffect(Effect):

    def __init__(self, delete):
        self.delete = delete

    def apply(self, state, out=None):
        raise NotImplementedError()

    def bind(self, sigma):
        return DeleteEffect(self.delete.bind(sigma))

    def modified_predicates(self):
        return set([self.delete.name])

    def modified_functions(self):
        return set()

    def __str__(self):
        return lisp_list_to_str("not", self.delete)


class AndEffect(Effect):

    def __init__(self, *effects):
        self.effects = effects

    def apply(self, state, out=None):
        if out is None: out = state.copy()
        for effect in self.effects:
            out = effect.apply(state, out)
        return out

    def bind(self, sigma):
        return AndEffect(*(a.bind(sigma) for a in self.effects))

    def modified_predicates(self):
        mp = set()
        for e in self.effects:
            mp.update(e.modified_predicates())
        return mp

    def modified_functions(self):
        mf = set()
        for e in self.effects:
            mf.update(e.modified_functions())
        return mf

    def __str__(self):
        return lisp_list_to_str("and", *self.effects)


class ForallEffect(Effect):

    def __init__(self, parameters, effect):
        self.parameters = parameters
        self.effect = effect

    def apply(self, state, out=None):
       raise NotImplementedError() 

    def bind(self, sigma):
        return TotalEffect(self.parameters.bind(sigma), self.effect.bind(sigma))

    def modified_predicates(self):
        return self.effect.modified_predicates()

    def modified_functions(self):
        return self.effect.modified_functions()

    def __str__(self):
        return "(forall ({}) {})".format(self.parameters, self.query)


class ConditionalEffect(Effect):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def apply(self, state, out=None):
        out = super().apply(state, out)
        lhs = self.lhs.eval(state)
        if lhs:
            out = rhs.apply(state, out)
        return out

    def bind(self, sigma):
        return ConditionalEffect(self.lhs.bind(sigma), self.rhs.bind(sigma))

    def modified_predicates(self):
        return self.rhs.modified_predicates()

    def modified_functions(self):
        return self.rhs.modified_functions()

    def __str__(self):
        return lisp_list_to_str("when", self.lhs, self.rhs)


class AssignmentEffect(Effect):

    def __init__(self, assignop, lhs, rhs):
        assert assignop in ("assign", "increase", "decrease", "scale-up", "scale-down")
        self.assignop = assignop
        self.lhs = lhs
        self.rhs = rhs

    def apply(self, state, out=None):
        raise NotImplementedError()

    def bind(self, sigma):
        return AssignmentEffect(self.assignop, self.lhs.bind(sigma),
                self.rhs.bind(sigma))

    def modified_predicates(self):
        return set()

    def modified_functions(self):
        return set([self.lhs.name])

    def __str__(self):
        return lisp_list_to_str(self.assignop, self.lhs, self.rhs)


class ProbabilisticEffect(Effect):

    def __init__(self, *effects):
        total_prob = 0
        for p, _ in effects:
            total_prob += p
        assert total_prob < (1+1e-6)
        self.effects = effects

    def __len__(self):
        return len(self.effects)

    def __getitem__(self, idx):
        return self.effects[idx]

    def __iter__(self):
        return self.effects.__iter__()

    def apply(self, state, out=None):
        if out is None: out = state.copy()
        r = random()
        acc = 0
        for p, e in self:
            acc += p
            if r < p:
                out = e.apply(state, out)
                break
        return out

    def bind(self, sigma):
        return ProbabilisticEffect(*((p,e.bind(sigma)) for p, e in self.effects))

    def modified_predicates(self):
        mp = set()
        for p, e in self.effects:
            mp.update(e.modified_predicates())
        return mp

    def modified_functions(self):
        mf = set()
        for p, e in self.effects:
            mf.update(e.modified_predicates())
        return mf

    def __str__(self):
        return "(probabilistic {})".format(" ".join(str(p)+" "+str(e) for p, e in self.effects))


####################
## DOMAIN OBJECTS ##
####################

class Action:

    def __init__(self, name, parameters=None, precondition=None, effect=None):
        self.name = name
        self.parameters = ObjectList() if parameters is None else parameters
        self.precondition = EmptyQuery() if precondition is None else precondition
        self.effect = EmptyEffect() if effect is None else effect

    def is_applicable(self, state):
        raise NotImplementedError()

    def apply(self, state):
        raise NotImplementedError()

    def bind(self, sigma):
        return Action(self.name, self.parameters.bind(sigma),
                self.precondition.bind(sigma), self.effect.bind(sigma))

    def modified_predicates(self):
        return self.effect.modified_predicates()

    def modified_functions(self):
        return self.effect.modified_functions()

    def __str__(self):
        return "(:action {}\n  :parameters ({})\n  :precondition {}\n  :effect {}\n)".format(
                self.name, self.parameters, self.precondition, self.effect)


class Domain:

    def __init__(self, name, requirements=None, types=None,
            predicates=None, functions=None, actions=None):
        self.name = name
        self.requirements = requirements
        self.type_hierarchy = None if types is None else to_type_hierarchy(types)
        self.predicates = predicates
        self.functions = functions 
        self.actions = actions

    def get_predicate_by_name(self, name):
        return get_functional_by_name(self.predicates, name)

    def get_function_by_name(self, name):
        return get_functional_by_name(self.functions, name)

    def get_static_predicates(self):
        modifiable_predicates = set()
        for a in self.actions:
            modifiable_predicates.update(a.modified_predicates())
        return get_static_functionals(self.predicates, modifiable_predicates)

    def get_static_functions(self):
        modifiable_functions = set()
        for a in self.actions:
            modifiable_functions.update(a.modified_functions())
        return get_static_functionals(self.functions, modifiable_functions)

    def __str__(self):
        ret = "(define (domain " + self.name + ")\n\n"
        if self.requirements is not None:
            ret += "(:requirements " + " ".join(self.requirements) + ")\n\n"
        if self.type_hierarchy is not None:
            ret += "(:types " + type_hierarchy_to_str(self.type_hierarchy) + ")\n\n"
        if self.predicates is not None:
            ret += "(:predicates\n  " + "\n  ".join(str(p) for p in self.predicates) + "\n)\n\n"
        if self.functions is not None:
            ret += "(:functions " + "\n".join(str(f) + ((" - " + t) if t else "") for f,t in self.functions.items()) + ")\n\n"            
        if self.actions is not None:
            ret += "\n\n".join(map(str, self.actions))
        ret += ")"
        return ret


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


def to_type_hierarchy(types):
    if isinstance(types, (list, tuple)):
        return {t: None for t in types}
    elif isinstance(types, dict):
        hierarchy = types.copy()
        for p in types.values():
            if p not in hierarchy and p != "object" and p is not None:
                hierarchy[p] = None
        return hierarchy
    raise Exception("wrong type")


def lisp_list_to_str(*args):
    return "({})".format(" ".join(str(a) for a in args))


def type_hierarchy_to_str(hierarchy):
    reverse_dict = {}
    for c,p in hierarchy.items():
        try:
            reverse_dict[p].append(c)
        except KeyError:
            reverse_dict[p] = [c]
    first = True
    s = ""
    for p,cs in reverse_dict.items():
        if not first: s += "\n"
        s += " ".join(cs)
        if p is not None: s += " - " + p
        first = False
    return s


def inferred_types(hierarchy, type_):
    inferred = []
    while type_ is not None and type_ != "object":
        inferred.append(type_)
        type_ = hierarchy[type_]
    inferred.append("object") # every type is descendent of object
    return inferred


def get_functional_by_name(functionals, name):
    if functionals is not None:
        for f in famunctionals:
            if f.name == name: return f
    raise ValueError("There is no functional with name " + name)


def get_static_functionals(functionals, modifiable):
    static_functionals = []
    if functionals is not None:
        for f in functionals:
            if f.name not in modifiable:
                static_functionals.append(f)
    return static_functionals

