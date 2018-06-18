from .determinization import AllOutcomeDeterminizer

from .imagine.imagine_state import ImagineState
from .pddl import SymbolicState, PredicateQuery, Predicate

class Agent:
 
    def __call__(self, simulator, verbose=False):
        self._reset()
        simulator.reset()
        simulator.start()
        timeout = False
        done = False
        found = True
        step = 0
        state = simulator.current_state
        if verbose:
            print("Starting...")
            # print("Initial state: ")
            # print(state)
        while not timeout and not done and found:
            action = self._step(state, simulator.timeout - simulator.elapsed())
            found = action is not None
            timestamp = "[{:.03f}s] ".format(simulator.elapsed())
            if found:
                step += 1
                done, timeout, state = simulator.step(action)
                if verbose:
                    # print(timestamp + "Executed ({})".format(" ".join(action)))
                    print(timestamp + "Executed ({}). State at step {}".format(
                        " ".join(action), step))
                    print(state)
            else: timeout = simulator.elapsed() > simulator.timeout
        if verbose:
            print(timestamp + "Stopped after {} step(s).".format(step), end=" ")
            if done: print("Success!")
            elif timeout: print("Timeout!")
            elif not found: print("Plan not found!")
        return timeout, done, simulator.elapsed(), step, state

    def _reset(self):
        raise NotImplementedError()

    def _step(self, state, remaining):
        raise NotImplementedError()


class SimpleDeterminizerAgent(Agent):

    def __init__(self, problem, determinizer, planner):
        self.problem = problem
        self.determinizer = determinizer 
        self.planner = planner
        self._partial_policy = None
        self.invokations = 0

    def _step(self, state, remaining):
        if state not in self._partial_policy:
            self.problem.init = state.to_initial_state()
            dproblem = self.determinizer(self.problem)
            result = self.planner(dproblem, timeout=remaining)
            self.invokations += 1
            if result["plan-found"]:
                next_state = dproblem.get_initial_state()
                for action in result["plan"]:
                    action_outcome = dproblem.domain.retrieve_action(*action)
                    _, _, base = self.determinizer.process_action_tuple(action)
                    self._partial_policy[next_state] = base
                    next_state = action_outcome.apply(next_state)
            # else:
                # print(self.determinizer.determinized_domain)
                # print(dproblem)
                # print(result["stdout"])
                # print(result["stderr"])
        base_action = self._partial_policy.get(state)
        return base_action

    def _reset(self):
        self._partial_policy = {}


class HindsightAgent(Agent):
   
    def __init__(self, problem, determinizer, planner, initial_calls=30,
            calls_per_pha=30, penalty=100):
        self.problem = problem
        self.determinizer = determinizer 
        self.planner = planner
        self.initial_calls = initial_calls
        self.calls_per_pha = calls_per_pha
        self.penalty = penalty
        self.invokations = 0
        # self._aodeterminizer = AllOutcomeDeterminizer()
        # self._aodeterminizer.set_domain(determinizer.original_domain)
        self._longest_prefix = []
        self._partial_policy = {}

    def _pha(self, state, remaining):
        self.problem.init = state.to_initial_state()
        plans = []
        for idx in range(self.initial_calls):
            # determinizer = self.determinizer if idx < self.initial_calls-1 else self._aodeterminizer
            determinizer = self.determinizer
            dproblem = determinizer(self.problem)
            result = self.planner(dproblem, timeout=remaining/(self.initial_calls-idx))
            if result["plan-found"]:
                _, plan = determinizer.process_plan_trace(result["plan"])
                plans.append(plan)
            # else:
                # print(dproblem)
                # print(self.determinizer.determinized_domain)
                # print(result["stdout"])
                # print(result["stderr"])
            remaining -= result["time-wall"]
            # print(idx)
        pha = group_by_first_action(plans)
        # scored_pha = sorted(pha.items(), key=lambda item: len(item[1]), reverse=True)[:self.max_pha]
        # scored_pha = sorted([(len(plan), a) for a,plan in pha.items()], reverse=True)[:self.max_pha]
        # print(scored_pha)
        return remaining, pha

    def _step(self, state, remaining):
        if self._longest_prefix:
            base_action = self._longest_prefix.pop()
        elif state in self._partial_policy:
            base_action = self._partial_policy[state]
        else:
            remaining, pha = self._pha(state, remaining)
            # print(pha)
            # remaining_invokations = self.calls_per_pha*len(pha)
            for a, plans in pha.items():
                del plans[:]
                action = self.problem.domain.retrieve_action(*a)
                for idx in range(self.calls_per_pha):
                    determinizer = self.determinizer
                    # determinizer = self._aodeterminizer if idx == self.calls_per_pha - 1 else self.determinizer
                    next_state = action.apply(state)
                    next_state.reward = None
                    self.problem.init = next_state.to_initial_state()
                    dproblem = determinizer(self.problem)
                    result = self.planner(dproblem, timeout=remaining)
                    if result["plan-found"]:
                        _, plan = self.determinizer.process_plan_trace(result["plan"])
                        plans.append(plan)
                    else:
                        # print(result["stdout"])
                        # print(result["stderr"])
                        plans.append(None)
                    remaining -= result["time-wall"]
                    # remaining_invokations -= 1
                    # print(remaining_invokations)
            scored_pha = {}
            for a, plans in pha.items():
                # scored_pha[a] = sum(1
                        # if p is not None else 0 for p in plans)/self.calls_per_pha
                scored_pha[a] = sum(-len(p) if p is not None else -self.penalty for p in plans)/self.calls_per_pha
            # print(scored_pha)
            # print({a: [None if p is None else len(p) for p in plans] for a,plans in pha.items()})
            base_action = max(scored_pha.keys(), key=lambda a: scored_pha[a], default=None)
            if base_action is not None:
                self._partial_policy[state] = base_action
                lgst = longest_prefix(pha[base_action])
                if lgst:
                    self._longest_prefix = lgst
                    self._longest_prefix.reverse()
            self.invokations += len(pha)*self.calls_per_pha
        return base_action
                
    def _reset(self):
        self._partial_policy = {}
        self._longest_prefix = []
        self.invokations = 0


class ImagineAgent(Agent):
    
    def __init__(self, agent):
        self.agent = agent
        self._last_executed = None
        self._repeated = 0
        self._top_priority = None
        self._ranking = {}

    def _update_ranking(self, state):
        for vertex, labels in state.graph.V.items():
            if "removed-verified" in labels:
                try:
                    del self._ranking[vertex]
                except KeyError:
                    pass
            elif "removable-component" in labels:
                self._ranking.setdefault(vertex,1)

    def _get_top_priority(self):
        if self._top_priority not in self._ranking:
            self._top_priority = None
        if self._top_priority is None or self._repeated > 3:
            if self._repeated > 4:
                self._ranking[self._top_priority] -= 1
                self._repeated = 0
                # print("Same action repeated too many times! Changing priority...")
            self._top_priority = max(self._ranking, key=self._ranking.__getitem__, default=None)
        return self._top_priority

    def _step(self, state, remaining):
        state.remove_occluded()
        self._update_ranking(state)
        top = self._get_top_priority()
        base_action = None
        if top:
            state.focus(top)
            self.agent.problem.objects = state.objects
            self.agent.problem.goal.query = PredicateQuery(Predicate("removed-verified", top))
            sym_state = SymbolicState(state.predicates)
            sym_state.reward = state.reward
            sym_state.problem = self.agent.problem
            base_action = self.agent._step(sym_state,remaining)
            if self._last_executed == base_action:
                self._repeated += 1
            self._last_executed = base_action
        return base_action

    def _reset(self):
        self._repeated = 0
        self._top_priority = None
        self._ranking = {}
        self.agent._reset()


def group_by_first_action(plans):
    grouped = {}
    for p in plans:
        first_action = p[0]
        try:
            grouped[first_action].append(p)
        except KeyError:
            grouped[first_action] = [p]
    return grouped


def intersect_plans(plan1, plan2):
    prefix = []
    for a1, a2 in zip(plan1,plan2):
        if a1 == a2:
            prefix.append(a1)
        else:
            break
    return prefix


def longest_prefix(plans):
    prefix = None
    for plan in plans:
        if plan is None: continue
        prefix = plan if prefix is None else intersect_plans(prefix, plan)
        if not prefix: break
    return prefix


