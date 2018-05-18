
from .pddl import *

from functools import reduce
from itertools import product


def all_outcome_determinization(domain):
    determinized = expand_domain(domain)
    actions = []
    for a in determinized.actions:
        for idx, (_, e) in enumerate(a.effect):
            anew = a.copy()
            anew.name = anew.name + "_o" + str(idx)
            anew.effect = e
            actions.append(anew)
    determinized.actions = actions
    return determinized


def single_outcome_determinization(problem):
    pass


#############
# UTILITIES #
#############

BASE_EFFECTS = (
    EmptyEffect,
    AddEffect,
    DeleteEffect,
    ForallEffect,
    ConditionalEffect,
    AssignmentEffect,
)


def expand_probabilistic_effects(effect):
    """
    Assumption: total and conditional effects won't have probabilistic effects
    inside (PPDDL would actually allow that). In such case, the effect cannot
    be expanded without grounding.
    """
    if isinstance(effect, BASE_EFFECTS):
        outcomes = [(1.0, effect)]
    elif isinstance(effect, AndEffect):
        possibilities = []
        for e in effect.effects:
            possibilities.append(expand_probabilistic_effects(e))
        outcomes = [(reduce(lambda acc, t: acc*t[0], outcome, 1.0),
            AndEffect(*(e for _, e in outcome)))
            for outcome in product(*possibilities)]
    elif isinstance(effect, ProbabilisticEffect):
        outcomes = []
        remaining = 1.0
        for p, e in effect.effects:
            remaining -= p
            outcomes += [(p*p_, e_)
                    for p_, e_ in expand_probabilistic_effects(e)]
        if remaining > 1e-6:
            outcomes.append((remaining, EmptyEffect()))
    else:
        raise Exception("unknown effect type: " + str(type(effect)))
    return outcomes


def expand_probabilistic_actions(actions):
    expanded = []
    for a in actions:
        peffect = ProbabilisticEffect(*expand_probabilistic_effects(a.effect))
        aexpanded = a.copy()
        aexpanded.effect = peffect
        expanded.append(aexpanded)
    return expanded


def expand_domain(domain):
    expanded = domain.copy()
    expanded.actions = expand_probabilistic_actions(domain.actions)
    return expanded

