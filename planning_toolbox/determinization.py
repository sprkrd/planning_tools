
from .pddl import *

from functools import reduce
from itertools import product

from math import log


def all_outcome_determinization(domain):
    determinized = remove_mdp_features(preprocess_domain(domain.copy()))
    actions = []
    for a in determinized.actions:
        assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
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
        assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
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


def alpha_cost_likelihood_determinization(domain, alpha=1.0, inters=0, round_=0):
    determinized = remove_mdp_features(preprocess_domain(domain.copy()))
    actions = []
    for a in determinized.actions:
        assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
        for idx, (p, e) in enumerate(a.effect):
            anew = a.copy()
            anew.name = anew.name + "_o" + str(idx)
            e = multiply_costs(e, alpha, round_)
            offset = inters - (log(p) if round_ == 0 else round(log(p)*10**round_))
            if offset > 0: e = add_cost_offset(e, offset)
            anew.effect = e
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
    AssignmentEffect,
)


def expand_probabilistic_effects(effect):
    """
    Assumption: total effects won't have probabilistic effects
    inside (PPDDL would actually allow that). In such case, the effect cannot
    be expanded without grounding.
    """
    if isinstance(effect, BASE_EFFECTS):
        outcomes = [(1.0, effect)]
    elif isinstance(effect, ConditionalEffect):
        outcomes = expand_probabilistic_effects(effect.rhs)
        outcomes = [(p, ConditionalEffect(effect.lhs, o)) for p,o in outcomes]
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
        aexpanded.effect = peffect.simplify()
        expanded_actions.append(aexpanded)
    domain.actions = expanded_actions
    return domain


def substitute_reward_by_total_cost(effect):
    if isinstance(effect, AndEffect):
        effect.effects = [substitute_reward_by_total_cost(e)
                for e in effect.effects]
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
                effect = EmptyEffect()
                # effect.assignop = "decrease"
    elif isinstance(effect, ProbabilisticEffect):
        effect.effects = [(p,substitute_reward_by_total_cost(e))
                for p,e in effect.effects]
    return effect


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
            a.effect = substitute_reward_by_total_cost(a.effect)
            a.effect = a.effect.simplify()
    return domain


def multiply_costs(effect, m=1.0, round_=0):
    if isinstance(effect, AssignmentEffect):
        if effect.lhs.name == "total-cost":
            if isinstance(effect.rhs, Constant):
                effect.rhs.constant = effect.rhs.constant*m
                if effect.rhs.constant < 0:
                    effect.assignop = "increase" if effect.assignop == "decrease" else "decrease"
                    effect.rhs.constant = -effect.rhs.constant
                if round_ > 0:
                    effect.rhs.constant = round(effect.rhs.constant*10**round_)
            # else:
                # effect.rhs = ArithmeticQuery("*", effect.rhs, m)
                # effect.rhs = ArithmeticQuery("+", effect.rhs, inters)
    elif isinstance(effect, AndEffect):
        effect.effects = [multiply_costs(e, m, round_) for e in effect.effects]
    elif isinstance(effect, ForallEffect):
        effect.effect = multiply_costs(effect.effect, m, round_)
    elif isinstance(effect, ConditionalEffect):
        effect.rhs = multiply_costs(effect.rhs, m, round_)
    elif isinstance(effect, ProbabilisticEffect):
        effect.effects = [(p,multiply_costs(e, round_)) for p,e in effect.effects]
    return effect


def add_cost_offset(effect, offset):
    assert offset > 0
    assign_effect = AssignmentEffect("increase", Function("total-cost"),
            Constant(offset))
    if isinstance(effect, AndEffect):
        found = False
        for e in effect.effects:
            if isinstance(e, AssignmentEffect) and e.lhs.name == "total-cost" \
                    and e.assignop == "increase" and isinstance(e.rhs, Constant):
                e.rhs.constant += offset
                found = True
                break
        if not found: effect.effects.append(assign_effect)
    else:
        effect = AndEffect(effect, assign_effect)
    return effect


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


# def minimum_cost_increment(effect):
    # minimum = 0
    # if isinstance(effect, AssignmentEffect):
        # if effect.lhs.name == "total-cost":
            # if isinstance(effect.rhs, Constant):
                # minimum effect.rhs.constant if effect.assignop == "increase" else -effect.rhs.constant
    # elif isinstance(effect, AndEffect):
        # minimum = min(minimum_cost_increment(e) for e in effect.effects)
    # elif isinstance(effect, ConditionalEffect):
        # minimum = minimum_cost_increment(effect.rhs)
    # elif isinstance(effect, ProbabilisticEffect):
        # minimum = min(minimum_cost_increment(e) for p,e in effect.effects)
    # return minimum


