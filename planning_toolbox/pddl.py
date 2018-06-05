#################
## BASIC TYPES ##
#################

from copy   import deepcopy
from functools import reduce
from itertools import product
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

    def copy(self):
        return deepcopy(self)

    def strip_type(self):
        return Object(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other.name == self.name 

    def __str__(self):
        if self.type is not None:
            return self.name + " - " + self.type
        return self.name


class ObjectList:

    def __init__(self, *objects):
        self.objects = [to_object(obj) for obj in objects]

    def bind(self, sigma):
        return ObjectList(*(obj.bind(sigma) for obj in self.objects))

    def copy(self):
        return deepcopy(self)

    def is_ground(self):
        return all(o.is_ground for o in self.objects)

    def strip_types(self):
        return ObjectList(*(obj.strip_type() for obj in self.objects))

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
        return hash(tuple(self.objects))

    def __str__(self):
        ret = ""
        first = True
        for obj, next_obj in zip(self.objects, (*self.objects[1:], None)):
            if not first: ret += " "
            ret += obj.name
            same_type = next_obj is not None and next_obj.type == obj.type
            if obj.type and not same_type:
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

    def copy(self):
        return deepcopy(self)

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

    def is_empty(self):
        raise NotImplementedError()

    def simplify(self):
        raise NotImplementedError()

    def copy(self):
        return deepcopy(self)


class EmptyQuery(Query):
    
    def eval(self, state):
        return True

    def bind(self, sigma):
        return self

    def is_empty(self):
        return True

    def simplify(self):
        return self

    def __str__(self):
        return "(and)"


class PredicateQuery(Query):

    def __init__(self, predicate):
        self.predicate = predicate

    def eval(self, state):
        return state.has_predicate(self.predicate)

    def bind(self, sigma):
        return PredicateQuery(self.predicate.bind(sigma))

    def is_empty(self):
        return False

    def simplify(self):
        return self

    def __str__(self):
        return str(self.predicate)


class FunctionQuery(Query):

    def __init__(self, function):
        self.function = function

    def eval(self, state):
        return state.get_function_value(self.function)

    def bind(self, sigma):
        return FunctionQuery(self.function.bind(sigma))

    def is_empty(self):
        return False

    def simplify(self):
        return self

    def __str__(self):
        return str(self.function)


class Constant(Query):

    def __init__(self, constant):
        self.constant = constant

    def eval(self, state):
        return self.constant

    def bind(self, sigma):
        return self

    def is_empty(self):
        return False

    def simplify(self):
        return self

    def __str__(self):
        return str(self.constant)


class ArithmeticQuery(Query):

    OPERATORS = ("+", "-", "*", "/")

    def __init__(self, operator, lhs, rhs):
        assert operator in ArithmeticQuery.OPERATORS
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

    def is_empty(self):
        return False

    def simplify(self):
        return self

    def __str__(self):
        return lisp_list_to_str(self.operator, self.lhs, self.rhs)


class ComparisonQuery(Query):

    OPERATORS = ("<", ">", "<=", "=", ">=")

    def __init__(self, comparison, lhs, rhs):
        assert comparison in ComparisonQuery.OPERATORS
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

    def is_empty(self):
        return False

    def simplify(self):
        return self

    def __str__(self):
        return lisp_list_to_str(self.comparison, self.lhs, self.rhs)


class AndQuery(Query):

    def __init__(self, *queries):
        self.queries = list(queries)

    def eval(self, state):
        return all(a.eval(state) for a in self.queries)

    def bind(self, sigma):
        return AndQuery(*(a.bind(sigma) for a in self.queries))

    def is_empty(self):
        return all(q.is_empty() for q in self.queries)

    def simplify(self):
        return simplify_and_or(self, "queries", EmptyQuery)

    def __str__(self):
        return lisp_list_to_str("and", *self.queries)


class OrQuery(Query):

    def __init__(self, *queries):
        self.queries = list(queries)

    def eval(self, state):
        return any(a.eval(state) for a in self.queries)

    def bind(self, sigma):
        return OrQuery(*(a.bind(sigma) for a in self.queries))

    def is_empty(self):
        return all(q.is_empty() for q in self.queries)

    def simplify(self):
        return simplify_and_or(self, "queries", OrQuery)

    def __str__(self):
        return lisp_list_to_str("or", *self.queries)


class NotQuery(Query):

    def __init__(self, negated):
        self.negated = negated

    def eval(self, state):
        return not self.negated.eval(state)

    def bind(self, sigma):
        return NotQuery(self.negated.bind(sigma))

    def is_empty(self):
        return self.negated.is_empty()

    def simplify(self):
        self.negated = self.negated.simplify()
        if self.negated.is_empty(): return EmptyQuery()
        return self

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

    def is_empty(self):
        return self.rhs.is_empty()

    def simplify(self):
        self.lhs = self.lhs.simplify()
        self.rhs = self.rhs.simplify()
        if self.rhs.is_empty(): return EmptyQuery()
        if self.lhs.is_empty(): return self.rhs
        return self

    def __str__(self):
        return lisp_list_to_str("imply", self.lhs, self.rhs)


class ForallQuery(Query):

    def __init__(self, parameters, query):
        self.parameters = parameters
        self.query = query

    def eval(self, state):
        return all(self.query.bind(sigma).eval(state)
                for sigma in all_possible_assignments(state.problem, self.parameters))


    def bind(self, sigma):
        return ForallQuery(self.parameters, self.query.bind(sigma))

    def is_empty(self):
        return self.query.is_empty()

    def simplify(self):
        self.query = self.query.simplify()
        if self.query.is_empty(): return EmptyQuery()
        return self

    def __str__(self):
        return "(forall ({}) {})".format(self.parameters, self.query)


class ExistsQuery(Query):

    def __init__(self, parameters, query):
        self.parameters = parameters
        self.query = query

    def eval(self, state):
        raise any(self.query.bind(sigma).eval(state)
                for sigma in all_possible_assignments(state.problem, self.parameters))

    def bind(self, sigma):
        return ExistsQuery(self.parameters.bind(sigma), self.query.bind(sigma))

    def is_emtpy(self):
        return self.query.is_empty()

    def simplify(self):
        self.query = self.query.simplify()
        if self.query.is_empty(): return EmptyQuery()
        return self

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

    def copy(self):
        return deepcopy(self)

    def count_additive_effects(self):
        raise NotImplementedError()

    def expand_probabilistic_effects(self):
        raise NotImplementedError()

    def is_empty(self):
        raise NotImplementedError()

    def modified_predicates(self):
        raise NotImplementedError()

    def modified_functions(self):
        raise NotImplementedError()

    def add_cost_offset(self, offset):
        assigeff = AssignmentEffect("increase", Function("total-cost"),
                Constant(offset))
        return AndEffect(self, assigeff)

    def transform_rewards_to_costs(self, alpha=1, inters=0, round_=0):
        raise NotImplementedError()

    def remove_reward_assignments(self):
        raise NotImplementedError()

    def simplify(self):
        raise NotImplementedError()


class EmptyEffect(Effect):

    def apply(self, state, out=None):
        return out or state.copy()

    def bind(self, sigma):
        return self

    def count_additive_effects(self):
        return 0

    def expand_probabilistic_effects(self):
        return ProbabilisticEffect((1.0, self))

    def is_empty(self):
        return True

    def modified_predicates(self):
        return set()

    def modified_functions(self):
        return set()

    def transform_rewards_to_costs(self, alpha=1, inters=0, round_=0):
        return self

    def remove_reward_assignments(self):
        return self

    def simplify(self):
        return self

    def __str__(self):
        return "(and)"


class AddEffect(Effect):

    def __init__(self, add):
        self.add = add

    def apply(self, state, out=None):
        out = out or state.copy()
        out.add_predicate(self.add)
        return out

    def bind(self, sigma):
        return AddEffect(self.add.bind(sigma))

    def count_additive_effects(self):
        return 1

    def expand_probabilistic_effects(self):
        return ProbabilisticEffect((1.0, self))

    def is_empty(self):
        return False

    def modified_predicates(self):
        return set([self.add.name])

    def modified_functions(self):
        return set()

    def transform_rewards_to_costs(self, alpha=1, inters=0, round_=0):
        return self

    def remove_reward_assignments(self):
        return self

    def simplify(self):
        return self

    def __str__(self):
        return str(self.add)


class DeleteEffect(Effect):

    def __init__(self, delete):
        self.delete = delete

    def apply(self, state, out=None):
        out = out or state.copy()
        out.delete_predicate(self.delete)
        return out

    def bind(self, sigma):
        return DeleteEffect(self.delete.bind(sigma))

    def count_additive_effects(self):
        return 0

    def expand_probabilistic_effects(self):
        return ProbabilisticEffect((1.0, self))

    def is_empty(self):
        return False

    def modified_predicates(self):
        return set([self.delete.name])

    def modified_functions(self):
        return set()

    def transform_rewards_to_costs(self, alpha=1, inters=0, round_=0):
        return self

    def remove_reward_assignments(self):
        return self

    def simplify(self):
        return self

    def __str__(self):
        return lisp_list_to_str("not", self.delete)


class AndEffect(Effect):

    def __init__(self, *effects):
        self.effects = list(effects)

    def apply(self, state, out=None):
        out = out or state.copy()
        for effect in self.effects:
            out = effect.apply(state, out)
        return out

    def bind(self, sigma):
        return AndEffect(*(a.bind(sigma) for a in self.effects))

    def count_additive_effects(self):
        return sum(e.count_additive_effects() for e in self.effects)

    def expand_probabilistic_effects(self):
        expanded_effects = [e.expand_probabilistic_effects() for e in self.effects]
        return ProbabilisticEffect(*[
            (reduce(lambda acc, t: acc*t[0], outcome, 1.0),
            AndEffect(*(e for p,e in outcome)))
            for outcome in product(*(e.effects for e in expanded_effects))
        ])

    def is_empty(self):
        if None in self.effects: print(self)
        return all(e.is_empty() for e in self.effects)

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

    def add_cost_offset(self, offset):
        found = False
        for e in self.effects:
            if isinstance(e, AssignmentEffect) and e.lhs.name == "total-cost" \
                    and e.assignop == "increase" and isinstance(e.rhs, Constant):
                e.rhs.constant += offset
                found = True
                break
        if not found:
            assigneff = AssignmentEffect("increase", Function("total-cost"),
                    Constant(offset))
            self.effects.append(assigneff)
        return self

    def transform_rewards_to_costs(self, alpha=1, inters=0, round_=0):
        self.effects = [e.transform_rewards_to_costs(alpha,inters,round_)
                for e in self.effects]
        return self

    def remove_reward_assignments(self):
        self.effects = [e.remove_reward_assignments() for e in self.effects]
        return self

    def simplify(self):
        effects = []
        for e in self.effects:
            if isinstance(e, AndEffect):
                effects += e.effects
            else:
                effects.append(e)
        self.effects = effects
        return simplify_and_or(self, "effects", EmptyEffect)

    def __len__(self):
        return len(self.effects)

    def __str__(self):
        return lisp_list_to_str("and", *self.effects)


class ForallEffect(Effect):

    def __init__(self, parameters, effect):
        self.parameters = parameters
        self.effect = effect

    def apply(self, state, out=None):
       out = out or state.copy()
       for sigma in all_possible_assignments(state.problem, self.parameters):
           out = self.effect.bind(sigma).apply(state, out)
       return out

    def bind(self, sigma):
        return TotalEffect(self.parameters.bind(sigma), self.effect.bind(sigma))

    def count_additive_effects(self):
        return self.effect.count_additive_effects()

    def expand_probabilistic_effects(self):
        """
        We assume that there are not nested probabilistic effects inside a
        total effect
        """
        return ProbabilisticEffect((1.0, self))

    def is_empty(self):
        return self.effect.is_empty()

    def modified_predicates(self):
        return self.effect.modified_predicates()

    def modified_functions(self):
        return self.effect.modified_functions()

    def transform_rewards_to_costs(self, alpha=1, inters=0, round_=0):
        self.effect = self.effect.transform_rewards_to_costs(alpha, inters, round_)
        return self

    def remove_reward_assignments(self):
        self.effect = self.effect.remove_reward_assignments()
        return self

    def simplify(self):
        self.effect = self.effect.simplify()
        if self.effect.is_empty(): return EmptyEffect()
        return self

    def __str__(self):
        return "(forall ({}) {})".format(self.parameters, self.effect)


class ConditionalEffect(Effect):

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def apply(self, state, out=None):
        out = out or state.copy()
        lhs = self.lhs.eval(state)
        if lhs:
            out = self.rhs.apply(state, out)
        return out

    def bind(self, sigma):
        return ConditionalEffect(self.lhs.bind(sigma), self.rhs.bind(sigma))

    def count_additive_effects(self):
        return self.rhs.count_additive_effects()

    def expand_probabilistic_effects(self):
        expanded = self.rhs.expand_probabilistic_effects()
        return ProbabilisticEffect(*((p, ConditionalEffect(self.lhs, e))
                for p,e in expanded))

    def is_empty(self):
        return self.rhs.is_empty()

    def modified_predicates(self):
        return self.rhs.modified_predicates()

    def modified_functions(self):
        return self.rhs.modified_functions()

    def transform_rewards_to_costs(self, alpha=1, inters=0, round_=0):
        self.rhs = self.rhs.transform_rewards_to_costs(alpha, inters, round_)
        return self

    def remove_reward_assignments(self):
        self.rhs = self.rhs.remove_reward_assignments()
        return self

    def simplify(self):
        self.lhs = self.lhs.simplify()
        self.rhs = self.rhs.simplify()
        if self.rhs.is_empty(): return EmptyEffect()
        if self.lhs.is_empty(): return self.rhs
        return self

    def __str__(self):
        return lisp_list_to_str("when", self.lhs, self.rhs)


class AssignmentEffect(Effect):

    OPERATORS = ("assign", "increase", "decrease", "scale-up", "scale-down")

    def __init__(self, assignop, lhs, rhs):
        assert assignop in AssignmentEffect.OPERATORS
        self.assignop = assignop
        self.lhs = lhs
        self.rhs = rhs
        if isinstance(rhs, int):
            import traceback
            traceback.print_stack()
            exit()

    def apply(self, state, out=None):
        out = out or state.copy()
        lhs = state.get_function_value(self.lhs)
        rhs = self.rhs.eval(state)
        if self.assignop == "assign": out.set_function_value(self.lhs, rhs)
        elif self.assignop == "increase": out.set_function_value(self.lhs, lhs+rhs)
        elif self.assignop == "decrease": out.set_function_value(self.lhs, lhs-rhs)
        elif self.assignop == "scale-up": out.set_function_value(self.lhs, lhs*rhs)
        else: out.set_function_value(self.lhs, lhs/rhs)
        return out

    def count_additive_effects(self):
        return 0

    def expand_probabilistic_effects(self):
        return ProbabilisticEffect((1.0, self))

    def bind(self, sigma):
        return AssignmentEffect(self.assignop, self.lhs.bind(sigma),
                self.rhs.bind(sigma))

    def is_empty(self):
        return False

    def modified_predicates(self):
        return set()

    def modified_functions(self):
        return set([self.lhs.name])

    def add_cost_offset(self, offset):
        if self.assignop == "increase" and self.lhs.name == "total-cost" and\
                isinstance(self.rhs, Constant):
            self.rhs.constant += offset
            return self
        return super().add_cost_offset(offset)

    def remove_reward_assignments(self):
        if self.lhs.name == "reward": return EmptyEffect()
        return self

    def transform_rewards_to_costs(self, alpha=1, inters=0, round_=0):
        if self.lhs.name == "reward":
            if self.assignop == "decrease":
                self.lhs.name = "total-cost"
                self.assignop = "increase"
                if isinstance(self.rhs, Constant):
                    self.rhs.constant = self.rhs.constant*alpha + inters
                    if round_ > 0: self.rhs.constant = int(round(self.rhs.constant*10**round_))
            else: return EmptyEffect()
        return self

    def simplify(self):
        return self

    def __str__(self):
        return lisp_list_to_str(self.assignop, self.lhs, self.rhs)


class ProbabilisticEffect(Effect):

    def __init__(self, *effects):
        total_prob = 0
        for p, _ in effects:
            total_prob += p
        assert total_prob < (1+1e-6)
        self.effects = list(effects)

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

    def count_additive_effects(self):
        return max(e.count_additive_effects() for _,e in self.effects)

    def expand_probabilistic_effects(self):
        outcomes = []
        remaining = 1.0
        for p,e in self.effects:
            remaining -= p
            outcomes += [(p*p_, e_)
                    for p_,e_ in e.expand_probabilistic_effects().effects]
        if remaining > 1e-6:
            outcomes.append((remaining, EmptyEffect()))
        return ProbabilisticEffect(*outcomes)
        
    def bind(self, sigma):
        return ProbabilisticEffect(*((p,e.bind(sigma)) for p, e in self.effects))

    def is_empty(self):
        return all(e.is_empty() for _,e in self.effects)

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

    def transform_rewards_to_costs(self, alpha=1, inters=0, round_=0):
        self.effects = [(p, e.transform_rewards_to_costs(alpha, inters, round_))
                for p,e in self.effects]
        return self

    def remove_reward_assignments(self):
        self.effects = [(p,e.remove_reward_assignments()) for p,e in self.effects]
        return self

    def simplify(self):
        self.effects = [(p,e.simplify()) for p,e in self.effects]
        # self.effects = [(p,e) for p,e in
                # map(lambda t: (t[0],t[1].simplify()), self.effects)
                # if not e.is_empty() and p > 1e-6]
        # if len(self.effects) == 1 and abs(self.effects[0][0] - 1) < 1e-6:
            # return self.effects[0][1]
        if not self.effects:
            return EmptyEffect()
        return self

    def sum_to_one(self):
        accprob = 0
        for p, _ in self.effects:
            accprob += p
        return abs(accprob - 1) < 1e-6

    def __len__(self):
        return len(self.effects)

    def __getitem__(self, idx):
        return self.effects[idx]

    def __iter__(self):
        return self.effects.__iter__()

    def __str__(self):
        return "(probabilistic {})".format(" ".join(str(p)+" "+str(e) for p, e in self.effects))


####################
## DOMAIN OBJECTS ##
####################

class Action:

    def __init__(self, name="", parameters=None, precondition=None, effect=None):
        self.name = name
        self.parameters = ObjectList() if parameters is None else parameters
        self.precondition = EmptyQuery() if precondition is None else precondition
        self.effect = EmptyEffect() if effect is None else effect

    def is_applicable(self, state):
        return self.precondition.eval(state)

    def apply(self, state):
        if self.precondition.eval(state):
            new_state = self.effect.apply(state)
            if state.problem.goal.reward and state.problem.goal.query.eval(new_state):
                new_state.reward += state.problem.goal.reward
            return new_state
        return None

    def bind(self, sigma):
        return Action(self.name, self.parameters.bind(sigma),
                self.precondition.bind(sigma), self.effect.bind(sigma))

    def copy(self):
        return deepcopy(self)

    def modified_predicates(self):
        return self.effect.modified_predicates()

    def modified_functions(self):
        return self.effect.modified_functions()

    def tuple_representation(self):
        return (self.name,*(obj.name for obj in self.parameters))

    def short_str(self):
        return "({})".format(" ".join(self.tuple_representation()))

    def __str__(self):
        ret = "(:action {}\n".format(self.name)
        if self.parameters: ret += "  :parameters ({})\n".format(self.parameters)
        if not self.precondition.is_empty(): ret += "  :precondition {}\n".format(self.precondition)
        if not self.effect.is_empty(): ret += "  :effect {}\n".format(self.effect)
        ret += ")"
        return ret

    def __repr__(self):
        return self.short_str()


class Domain:

    def __init__(self, name="", requirements=None, types=None, constants=None,
            predicates=None, functions=None, actions=None):
        self.name = name
        self.requirements = [] if requirements is None else requirements
        self.type_hierarchy = {} if types is None else to_type_hierarchy(types)
        self.constants = ObjectList() if constants is None else constants
        self.predicates = [] if predicates is None else predicates
        self.functions = [] if functions is None else functions
        self.actions = [] if actions is None else actions

    def allows_equality_predicate(self):
        return ":equality" in self.requirements or ":adl" in self.requirements

    def allows_reward_fluent(self):
        return ":rewards" in self.requirements or ":mdp" in self.requirements

    def all_predicates(self):
        allpred = self.predicates.copy()
        if self.allows_equality_predicate():
            allpred.append(Predicate("=", "?x", "?y"))
        return allpred

    def all_functions(self):
        allfuncs = self.functions.copy()
        if self.allows_reward_fluent():
            allfuncs.append(Function("reward"))
        return allfuncs

    def retrieve_action(self, name, *args):
        action = None
        for a in self.actions:
            if a.name == name:
                action = a
                if args:
                    action = a.bind({param.name: arg
                        for param,arg in zip(a.parameters, args)})
        return action

    def get_static_predicates(self):
        modifiable = set()
        for a in self.actions:
            modifiable.update(a.modified_predicates())
        static = [p for p in self.all_predicates() if p.name not in modifiable]
        return static

    def get_static_functions(self):
        modifiable = set()
        # the reward fluent, if present, should be considered modifiable
        modifiable.add("reward")
        for a in self.actions:
            modifiable.update(a.modified_functions())
        return [f for f in self.all_functions() if f.name not in modifiable]

    def copy(self):
        return deepcopy(self)

    def expand_probabilistic_effects(self):
        for a in self.actions:
            a.effect = a.effect.expand_probabilistic_effects().simplify()
        return self

    def remove_reward_assignments(self):
        for a in self.actions:
            a.effect = a.effect.remove_reward_assignments().simplify()
        return self

    def remove_mdp_requirements(self):
        for req in (":probabilistic-effects", ":rewards", ":mdp"):
            try:
                self.requirements.remove(req)
            except ValueError:
                pass
        return self
        
    def __str__(self):
        ret = "(define (domain " + self.name + ")\n\n"
        if self.requirements:
            ret += "(:requirements " + " ".join(self.requirements) + ")\n\n"
        if self.type_hierarchy:
            ret += "(:types " + type_hierarchy_to_str(self.type_hierarchy) + ")\n\n"
        if self.constants:
            ret += "(:constants " + str(self.constants) + ")\n\n"
        if self.predicates:
            ret += "(:predicates\n  " + "\n  ".join(str(p) for p in self.predicates) + "\n)\n\n"
        if self.functions:
            ret += "(:functions " + "\n".join(str(f) for f in self.functions) + ")\n\n"            
        ret += "\n\n".join(map(str, self.actions)) + ")"
        return ret


class Goal:

    def __init__(self, query=None, reward=None, metric=None):
        self.query = query
        self.reward = reward
        self.metric = metric

    def copy(self):
        return deepcopy(self)

    def __str__(self):
        ret = ""
        if self.query: ret += "(:goal {})\n".format(self.query)
        if self.reward: ret += "(:goal-reward {})\n".format(self.reward)
        if self.metric: ret += "(:metric {} {})\n".format(*self.metric)
        return ret


class InitialState:

    def __init__(self, predicates=None, functions=None, probabilistic=None):
        self.predicates = [] if predicates is None else predicates
        self.functions = {} if functions is None else functions
        self.probabilistic = [] if probabilistic is None else probabilistic

    def copy(self):
        return deepcopy(self)

    def get_state(self):
        # [TODO] Probabilistic
        return SymbolicState(self.predicates, self.functions)

    def erase_reward(self):
        try: del self.functions[Function("reward")]
        except KeyError: pass

    def __str__(self):
        ret = "(:init\n  "
        ret += "\n  ".join(str(p) for p in self.predicates) + "\n"
        for f,v in self.functions.items():
            ret += "  (= {} {})\n".format(f, v)
        for plist in self.probabilistic:
            ret += "  (probabilistic"
            for prob, v in plist:
                ret += " " + str(prob)
                if isinstance(v, (list, tuple)):
                    ret += " " + "(and {})".format(" ".join(str(p) for p in v))
                else:
                    ret += " " + str(v)
            ret += ")\n"
        ret += ")\n"
        return ret


class Problem:

    def __init__(self, name="", domain=None, objects=None, init=None, goal=None):
        self.name = name
        self.domain = domain
        self.objects = ObjectList() if objects is None else objects
        self.init = InitialState() if init is None else init
        self.goal = Goal(EmptyQuery()) if goal is None else goal

    def all_objects_of_type(self, type_=None):
        objects_of_type = []
        for obj in self.objects:
            inferred = inferred_types(self.domain.type_hierarchy, obj.type)
            if type_ in inferred: objects_of_type.append(obj.name)
        return objects_of_type

    def ground_operators(self):
        for action in self.domain.actions:
            for sigma in all_possible_assignments(self, action.parameters):
                yield action.bind(sigma)

    def get_initial_state(self):
        s0 = self.init.get_state()
        s0.problem = self
        if self.domain.allows_reward_fluent(): s0.reward = 0
        return s0

    def copy(self):
        return Problem(self.name, self.domain, self.objects.copy(),
                self.init.copy(), self.goal.copy())

    def remove_mdp_features(self):
        self.goal.reward = None
        if self.goal.metric:
            metricfun = self.goal.metric[1]
            if isinstance(metricfun, FunctionQuery) and metricfun.function.name == "reward":
                self.goal.metric = None
        self.init.erase_reward()
        return self

    def __str__(self):
        ret = "(define (problem {})\n".format(self.name)
        if self.domain is not None:
            ret += "(:domain {})\n".format(self.domain.name)
        ret += "(:objects {})\n".format(self.objects)
        ret += str(self.init)
        ret += str(self.goal)
        ret += ")"
        return ret


class SymbolicState:

    def __init__(self, predicates=None, functions=None, problem=None):
        self.predicates = set() if predicates is None else set(predicates)
        self.total_cost = None
        self.reward = None
        if functions is not None:
            for fun, val in functions.items():
                self.set_function_value(fun, val)
        self.problem = problem
        self._hash = None

    def add_predicate(self, predicate):
        self.predicates.add(predicate)
        self._hash = None

    def delete_predicate(self, predicate):
        self.predicates.discard(predicate)
        self._hash = None

    def copy(self):
        clone = SymbolicState(self.predicates.copy(), problem=self.problem)
        clone.total_cost = self.total_cost
        clone.reward = self.reward
        return clone

    def has_predicate(self, predicate):
        if predicate.name == "=": return predicate.arguments[0] == predicate.arguments[1]
        return predicate in self.predicates

    def set_function_value(self, function, value):
        if function.name == "total-cost":
            self.total_cost = value
        elif function.name == "reward":
            self.reward = value
        else:
            raise Exception("Arbitrary functions not implemented")

    def get_function_value(self, function):
        if function.name == "total-cost":
            return self.total_cost
        if function.name == "reward":
            return self.reward
        raise Exception("Non-supported function: {}".format(function.name))

    def applicable_actions(self):
        for grop in self.problem.ground_operators():
            if grop.is_applicable(self):
                yield grop

    def to_initial_state(self):
        functions = {}
        if self.total_cost is not None:
            functions[Function("total-cost")] = self.total_cost
        if self.reward is not None:
            functions[Function("reward")] = self.reward
        return InitialState(list(self.predicates), functions)

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(frozenset(self.predicates))
        return self._hash

    def __eq__(self, other):
        return self.predicates == other.predicates

    def __str__(self):
        ret = "State from problem " + self.problem.name + ":\n  "
        ret += "\n  ".join(p for p in sorted(str(p_) for p_ in self.predicates))
        # if self.total_cost is not None:
        ret += "\n  Total cost: " + str(self.total_cost)
        # if self.reward is not None:
        ret += "\n  Reward: " + str(self.reward)
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


def simplify_and_or(obj, attr, empty_class):
    l = getattr(obj, attr)
    l = [e for e in map(lambda e: e.simplify(), l) if not e.is_empty()]
    setattr(obj, attr, l)
    if len(l) == 1: return l[0]
    if not l: return empty_class()
    return obj


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


def all_possible_assignments(problem, objlist):
    objects = []
    for obj in objlist:
        objects.append(problem.all_objects_of_type(obj.type))
    varnames = [obj.name for obj in objlist]
    return (dict(zip(varnames, values)) for values in product(*objects))

