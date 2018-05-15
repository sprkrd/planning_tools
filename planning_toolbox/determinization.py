
from .pddl import *

from functools import reduce
from itertools import product


#############
# UTILITIES #
#############

def expand_probabilistic_effects(effect):
    """
    Assumption: total and conditional effects won't have probabilistic effects
    inside (PPDDL would actually allow that). In such case, the effect cannot
    be expanded without grounding.
    """
    if isinstance(effect, (EmptyEffect, AddEffect, DeleteEffect, ForallEffect, ConditionalEffect, AssignmentEffect)):
        outcomes = [(1.0, effect)]
    elif isinstance(effect, AndEffect):
        possibilities = []
        for e in effect.effects:
            possibilities.append(expand_probabilistic_effects(e))
        outcomes = [(reduce(lambda acc, t: acc*t[0], outcome, 1.0)
                    for outcome in product(*possibilities))]
    elif isinstance(effect, ProbabilisticEffect):
        outcomes = []
        remaining = 1.0
        for p, e in effect.effects:
            remaining -= p
            possibilities += [(p*p_, e_) for p_, e_ in expand_probabilistic_effects(e)]
        if remaining > 1e-6:
            possibilities.append((remaining, EmptyEffect()))
    else:
        raise Exception("unknown effect type: " + str(type(effect)))
    return outcomes



