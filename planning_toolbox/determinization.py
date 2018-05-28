
from .pddl import *

from functools import reduce
from itertools import product

from math import log


class Determinizer:

    def set_domain(self, original_domain):
        self.original_domain = original_domain
        self.preprocessed_domain = original_domain.copy().expand_probabilistic_effects()
        self.determinized_domain = self.determinize_domain(self.preprocessed_domain.copy())

    def determinize_domain(self, domain):
        raise NotImplementedError()

    def determinize_problem(self, problem):
        raise NotImplementedError()

    def __call__(self, problem):
        return self.determinize_problem(problem)


class AllOutcomeDeterminizer(Determinizer):

    def determinize_domain(self, domain):
        domain = domain.remove_mdp_requirements()
        domain = domain.expand_probabilistic_effects()
        domain = domain.remove_reward_assignments()
        actions = []
        for a in domain.actions:
            assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
            for idx, (_, e) in enumerate(a.effect):
                anew = a.copy()
                anew.name = anew.name + "_o" + str(idx)
                anew.effect = e
                actions.append(anew)
        domain.actions = actions
        return domain
        

class SingleOutcomeDeterminizer(Determinizer):

    def __init__(self, strategy="mlo"):
        """
        mlo: most likely outcome
        mae: most additive effects
        """
        assert strategy in ("mlo", "mae")
        self.strategy = strategy

    def determinize_domain(self, domain):
        domain.remove_mdp_requirements()
        domain.expand_probabilistic_effects()
        domain.remove_reward_assignments()
        actions = []
        for a in domain.actions:
            assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
            selected_outcome = None
            for idx, (p, e) in enumerate(a.effect):
                score = p if self.strategy == "mlo" else e.count_additive_effects()
                if selected_outcome is None or score > selected_outcome[1]:
                    selected_outcome = (idx, score, e)
            anew = a.copy()
            anew.name = anew.name + "_o" + str(selected_outcome[0])
            anew.effect = selected_outcome[2]
            actions.append(anew)
        domain.actions = actions
        return domain


class AlphaCostLikelihoodDeterminizer(Determinizer):
    pass



def all_outcome_determinization(domain):
    domain.remove_mdp_requirements()
    domain.expand_probabilistic_effects()
    domain.remove_reward_assignments()
    actions = []
    for a in domain.actions:
        assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
        for idx, (_, e) in enumerate(a.effect):
            anew = a.copy()
            anew.name = anew.name + "_o" + str(idx)
            anew.effect = e
            actions.append(anew)
    domain.actions = actions
    return domain


def single_outcome_determinization(domain, strategy="mlo"):
    """
    mlo: most likely outcome
    mae: most additive effects
    """
    assert strategy in ("mlo", "mae")
    domain.remove_mdp_requirements()
    domain.expand_probabilistic_effects()
    domain.remove_reward_assignments()
    actions = []
    for a in domain.actions:
        assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
        selected_outcome = None
        for idx, (p, e) in enumerate(a.effect):
            score = p if strategy == "mlo" else e.count_additive_effects()
            if selected_outcome is None or score > selected_outcome[1]:
                selected_outcome = (idx, score, e)
        anew = a.copy()
        anew.name = anew.name + "_o" + str(selected_outcome[0])
        anew.effect = selected_outcome[2]
        actions.append(anew)
    domain.actions = actions
    return domain


def alpha_cost_likelihood_determinization(domain, alpha=1.0, base=0, round_=0):
    domain.remove_mdp_requirements()
    domain.expand_probabilistic_effects()
    actions = []
    for a in domain.actions:
        assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
        for idx, (p, e) in enumerate(a.effect):
            anew = a.copy()
            anew.name = anew.name + "_o" + str(idx)
            anew.effect = e.copy().transform_rewards_to_costs(alpha, round_=round_)
            offset = base - log(p)
            if round_ > 0: offset = round(offset*10**round_)
            if offset > 1e-6: anew.effect = anew.effect.add_cost_offset(offset)
            actions.append(anew)
    domain.actions = actions
    return domain


#############
# UTILITIES #
#############

