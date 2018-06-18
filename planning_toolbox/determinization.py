
from .pddl import *

from functools import reduce
from itertools import product

from math import log
import random

import re


class Determinizer:

    RE_ACTION = re.compile(r"([a-zA-Z0-9_\-]+)_o([0-9]+)")

    def set_domain(self, original_domain):
        self.original_domain = original_domain
        self.preprocessed_domain = original_domain.copy().expand_probabilistic_effects()
        self.determinized_domain = self.determinize_domain(self.preprocessed_domain.copy())

    def reset(self):
        self.set_domain(self.original_domain)

    def determinize_domain(self, domain):
        raise NotImplementedError()

    def determinize_problem(self, problem):
        raise NotImplementedError()

    def process_action_tuple(self, action_tuple):
        m = Determinizer.RE_ACTION.match(action_tuple[0])
        action_base = (m.group(1), *action_tuple[1:])
        action = self.preprocessed_domain.retrieve_action(*action_base)
        outcome = int(m.group(2))
        probability = action.effect[outcome][0]
        return outcome, probability, action.tuple_representation()

    def process_plan_trace(self, plan):
        probability = 1.0
        processed_plan = []
        for a in plan:
            m = Determinizer.RE_ACTION.match(a[0])
            _, p, action = self.process_action_tuple(a)
            probability *= p
            processed_plan.append(action)
        return probability, processed_plan

    def __call__(self, problem):
        determinized_problem = self.determinize_problem(problem.copy())
        determinized_problem.domain = self.determinized_domain
        return determinized_problem


class AllOutcomeDeterminizer(Determinizer):

    def determinize_domain(self, domain):
        domain = domain.remove_mdp_requirements()
        domain = domain.expand_probabilistic_effects()
        domain = domain.remove_reward_assignments()
        actions = []
        for a in domain.actions:
            assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
            for idx, (p, e) in enumerate(a.effect):
                if e.is_empty() or p < 1e-6: continue
                anew = a.copy()
                anew.name = anew.name + "_o" + str(idx)
                anew.effect = e.simplify()
                actions.append(anew)
        domain.actions = actions
        return domain

    def determinize_problem(self, problem):
        problem.remove_mdp_features()
        return problem
        

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
                if e.is_empty() or p < 1e-6: continue
                score = p if self.strategy == "mlo" else e.count_additive_effects()
                if selected_outcome is None or score > selected_outcome[1]:
                    selected_outcome = (idx, score, e)
            anew = a.copy()
            anew.name = anew.name + "_o" + str(selected_outcome[0])
            anew.effect = selected_outcome[2].simplify()
            actions.append(anew)
        domain.actions = actions
        return domain

    def determinize_problem(self, problem):
        problem.remove_mdp_features()
        return problem


class AlphaCostLikelihoodDeterminizer(Determinizer):

    def __init__(self, alpha=1, base=0, round_=0):
        self.alpha = alpha
        self.base = base
        self.round_ = round_

    def determinize_domain(self, domain):
        domain.remove_mdp_requirements()
        if "total-cost" not in (f.name for f in domain.functions):
            domain.functions.append(Function("total-cost"))
        actions = []
        for a in domain.actions:
            assert isinstance(a.effect, ProbabilisticEffect), str(type(a.effect))
            for idx, (p, e) in enumerate(a.effect):
                if e.is_empty() or p < 1e-6: continue
                anew = a.copy()
                anew.name = anew.name + "_o" + str(idx)
                anew.effect = e.copy().transform_rewards_to_costs(
                        self.alpha, round_=self.round_)
                offset = self.base - log(p)
                if self.round_ > 0: offset = int(round(offset*10**self.round_))
                if offset > 1e-6: anew.effect = anew.effect.add_cost_offset(offset)
                # don't consider actions that only increase the total cost
                # and don't modify the state in any other way
                anew.effect = anew.effect.simplify()
                if not (isinstance(anew.effect, AssignmentEffect) and
                        anew.effect.lhs.name == "total-cost"):
                    actions.append(anew)
        domain.actions = actions
        return domain

    def determinize_problem(self, problem):
        problem.remove_mdp_features()
        tcfun = Function("total-cost")
        problem.init.functions[tcfun] = 0
        problem.goal.metric = ("minimize", tcfun)
        return problem


class HindsightDeterminizer(Determinizer):
    
    def __init__(self, method="global", wheel_size=10, transform_rewards=False):
        assert method in ("global", "local")
        self.method = method
        self.wheel_size = wheel_size
        self.transform_rewards = transform_rewards

    def _determinize_domain_global(self, domain):
        domain.remove_mdp_requirements()
        if self.transform_rewards:
            if "total-cost" not in (f.name for f in domain.functions):
                domain.functions.append(Function("total-cost"))
        else: domain.remove_reward_assignments()
        domain.type_hierarchy["timestep"] = None
        domain.predicates.append(Predicate("current_timestep", ("?t", "timestep")))
        domain.predicates.append(Predicate("next_timestep",
            ("?tn_1", "timestep"), ("?tn", "timestep")))
        actions = []
        for a in domain.actions:
            for idx, (p, e) in enumerate(a.effect):
                if p < 1e-6: continue
                anew = a.copy()
                anew.name += "_o" + str(idx)
                anew.effect = e.copy()
                if self.transform_rewards:
                    anew.effect = anew.effect.transform_rewards_to_costs()
                anew.parameters.objects.append(Object("?tn_1", "timestep"))
                anew.parameters.objects.append(Object("?tn", "timestep"))
                new_queries = [
                        PredicateQuery(Predicate("current_timestep", "?tn_1")),
                        PredicateQuery(Predicate("next_timestep", "?tn_1", "?tn")),
                ]
                if len(a.effect) > 1:
                    applicable_pred = "applicable_" + anew.name
                    domain.predicates.append(Predicate(applicable_pred, ("?t", "timestep")))
                    new_queries.append(PredicateQuery(Predicate(applicable_pred, "?tn_1")))
                new_effects = [
                        DeleteEffect(Predicate("current_timestep", "?tn_1")),
                        AddEffect(Predicate("current_timestep", "?tn")),
                ]
                if isinstance(anew.precondition, AndQuery):
                    anew.precondition.queries += new_queries
                else:
                    anew.precondition = AndQuery(anew.precondition, *new_queries)
                if isinstance(anew.effect, AndEffect):
                    anew.effect.effects += new_effects
                else:
                    anew.effect = AndEffect(anew.effect, *new_effects)
                anew.effect = anew.effect.simplify()
                actions.append(anew)
        domain.actions = actions
        return domain

    def _determinize_domain_local(self, domain):
        domain.remove_mdp_requirements()
        if self.transform_rewards:
            if "total-cost" not in (f.name for f in domain.functions):
                domain.functions.append(Function("total-cost"))
        else: domain.remove_reward_assignments()
        domain.type_hierarchy["status"] = None
        domain.predicates.append(Predicate("next_status",
            ("?sn_1", "status"), ("?sn", "status")))
        actions = []
        for a in domain.actions:
            if len(a.effect) > 1:
                domain.predicates.append(Predicate("status_"+a.name, ("?s", "status")))
            for idx, (p, e) in enumerate(a.effect):
                if p < 1e-6: continue
                anew = a.copy()
                anew.name += "_o" + str(idx)
                anew.effect = e.copy()
                if self.transform_rewards:
                    anew.effect = anew.effect.transform_rewards_to_costs()
                if len(a.effect) > 1:
                    anew.parameters.objects.append(Object("?sn_1", "status"))
                    anew.parameters.objects.append(Object("?sn", "status"))
                    domain.predicates.append(Predicate("applicable_"+anew.name, ("?s", "status")))
                    new_queries = [
                            PredicateQuery(Predicate("status_"+a.name, "?sn_1")),
                            PredicateQuery(Predicate("applicable_"+anew.name, "?sn_1")),
                            PredicateQuery(Predicate("next_status", "?sn_1", "?sn")),
                    ]
                    new_effects = [
                            DeleteEffect(Predicate("status_"+a.name, "?sn_1")),
                            AddEffect(Predicate("status_"+a.name, "?sn")),
                    ]
                    if isinstance(anew.precondition, AndQuery):
                        anew.precondition.queries += new_queries
                    else:
                        anew.precondition = AndQuery(anew.precondition, *new_queries)
                    if isinstance(anew.effect, AndEffect):
                        anew.effect.effects += new_effects
                    else:
                        anew.effect = AndEffect(anew.effect, *new_effects)
                anew.effect = anew.effect.simplify()
                actions.append(anew)
        domain.actions = actions
        return domain

    def determinize_domain(self, domain):
        if self.method == "local":
            return self._determinize_domain_local(domain)
        return self._determinize_domain_global(domain)

    def _determinize_problem_global(self, problem):
        for idx in range(self.wheel_size):
            problem.objects.objects.append(Object("t"+str(idx), "timestep"))
        problem.init.predicates.append(Predicate("current_timestep", "t0"))
        for idx in range(self.wheel_size-1):
            problem.init.predicates.append(
                    Predicate("next_timestep", "t"+str(idx), "t"+str(idx+1)))
        problem.init.predicates.append(
                Predicate("next_timestep", "t"+str(self.wheel_size-1), "t0"))
        for a in self.preprocessed_domain.actions:
            if len(a.effect) > 1:
                for t in range(self.wheel_size):
                    outcome = sample_outcome(a)
                    problem.init.predicates.append(
                            Predicate("applicable_"+outcome, "t"+str(t)))
        return problem

    def _determinize_problem_local(self, problem):
        for idx in range(self.wheel_size):
            problem.objects.objects.append(Object("s"+str(idx), "status"))
        for a in self.preprocessed_domain.actions:
            if len(a.effect) > 1:
                problem.init.predicates.append(Predicate("status_"+a.name, "s0"))
        for idx in range(self.wheel_size-1):
            problem.init.predicates.append(
                    Predicate("next_status", "s"+str(idx), "s"+str(idx+1)))
        problem.init.predicates.append(
                Predicate("next_status", "s"+str(self.wheel_size-1), "s0"))
        for a in self.preprocessed_domain.actions:
            if len(a.effect) > 1:
                for s in range(self.wheel_size):
                    outcome = sample_outcome(a)
                    problem.init.predicates.append(
                            Predicate("applicable_"+outcome, "s"+str(s)))
        return problem

    def determinize_problem(self, problem):
        problem.remove_mdp_features()
        if self.transform_rewards:
            tcfun = Function("total-cost")
            problem.init.functions[tcfun] = 0
            problem.goal.metric = ("minimize", tcfun)
        if self.method == "local":
            return self._determinize_problem_local(problem)
        return self._determinize_problem_global(problem)


#############
# UTILITIES #
#############


def sample_outcome(action):
    # return action.name+"_o{}".format(random.randrange(len(action.effect)))
    r = random.random()
    acc = 0
    for idx, (p,e) in enumerate(action.effect):
        acc += p
        if r < acc:
            return action.name + "_o{}".format(idx)
    return action.name + "_o{}".format(len(action.effect)-1)


