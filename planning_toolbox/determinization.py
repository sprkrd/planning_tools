
from .pddl import *

from functools import reduce
from itertools import product


def all_outcome_determinization(domain):
    determinized = remove_mdp_features(preprocess_domain(domain.copy()))
    actions = []
    for a in determinized.actions:
        assert isinstance(a.effect, ProbabilisticEffect)
        for idx, (_, e) in enumerate(a.effect):
            anew = a.copy()
            anew.name = anew.name + "_o" + str(idx)
            anew.effect = e
            actions.append(anew)
    determinized.actions = actions
    return determinized


def single_outcome_determinization(domain, strategy="mlo"):
    """
    mlo: most likely outcome
    mae: most additive effects
    """
    assert strategy in ("mlo", "mae")
    determinized = remove_mdp_features(preprocess_domain(domain.copy()))
    actions = []
    for a in determinized.actions:
        assert isinstance(a.effect, ProbabilisticEffect)
        selected_outcome = None
        for idx, (p, e) in enumerate(a.effect):
            score = p if strategy == "mlo" else count_additive_effects(e)
            if selected_outcome is None or score > selected_outcome[1]:
                selected_outcome = (idx, score, e)
        anew = a.copy()
        anew.name = anew.name + "_o" + str(selected_outcome[0])
        anew.effect = selected_outcome[2]
        actions.append(anew)
    determinized.actions = actions
    return determinized


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


def preprocess_domain(domain):
    expanded_actions = []
    for a in domain.actions:
        peffect = ProbabilisticEffect(*expand_probabilistic_effects(a.effect))
        aexpanded = a.copy()
        aexpanded.effect = peffect
        expanded_actions.append(aexpanded)
    domain.actions = expanded_actions
    return domain


def substitute_reward_by_total_cost(effect):
    if isinstance(effect, AndEffect):
        for e in effect.effects:
            substitute_reward_by_total_cost(e)
    elif isinstance(effect, ForallEffect):
        substitute_reward_by_total_cost(effect.effect)
    elif isinstance(effect, ConditionalEffect):
        substitute_reward_by_total_cost(effect.rhs)
    elif isinstance(effect, AssignmentEffect):
        if effect.lhs.name == "reward":
            effect.lhs.name = "total-cost"
            if effect.assignop == "decrease":
                effect.assignop = "increase"
            elif effect.assignop == "increase":
                effect.assignop = "decrease"
    elif isinstance(effect, ProbabilisticEffect):
        for _,e in effect.effects:
            substitute_reward_by_total_cost(e)


def remove_mdp_features(domain):
    rewards = domain.allows_reward_fluent()
    for req in (":probabilistic-effects", ":rewards", ":mdp"):
        try:
            domain.requirements.remove(req)
        except ValueError:
            pass
    if rewards:
        if ":fluents" not in domain.requirements:
            domain.requirements.append(":fluents")
        if not any(f.name == "total-cost" for f in domain.functions):
            domain.functions.append(Function("total-cost"))
        for a in domain.actions:
            substitute_reward_by_total_cost(a.effect)
    return domain


def count_additive_effects(effect):
    if isinstance(effect, AddEffect):
        return 1
    if isinstance(effect, (EmptyEffect, DeleteEffect, AssignmentEffect)):
        return 0
    if isinstance(effect, AndEffect):
        return sum(count_additive_effects(e) for e in effect.effects)
    if isinstance(effect, ForallEffect):
        return count_additive_effects(effect.effect)
    if isinstance(effect, ConditionalEffect):
        return count_additive_effects(effect.rhs)
    if isinstance(effect, ProbabilisticEffect):
        return max(count_additive_effects(e) for p,e in effect.effects)
    raise Exception("unknown effect type: " + str(type(effect)))

