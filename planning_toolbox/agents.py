from .determinization import AllOutcomeDeterminizer

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
            print("Initial state: ")
            print(state)
        while not timeout and not done and found:
            action = self._step(state, simulator.timeout - simulator.elapsed())
            found = action is not None
            timestamp = "[{:.03f}s] ".format(simulator.elapsed())
            if found:
                step += 1
                done, timeout, state = simulator.step(action)
                if verbose:
                    print(timestamp + "Executed ({}). State at step {}".format(
                        " ".join(action), step))
                    print(state)
            else: timeout = simulator.elapsed() > simulator.timeout
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
        # self._last_plan = None
        # self._expected_state = None

    def _step(self, state, remaining):
        if state not in self._partial_policy:
            dproblem = self.determinizer(self.problem)
            self.problem.init = state.to_initial_state()
            result = self.planner(dproblem, timeout=remaining)
            if result["plan-found"]:
                next_state = dproblem.get_initial_state()
                for action in result["plan"]:
                    action_outcome = dproblem.domain.retrieve_action(*action)
                    _, _, base = self.determinizer.process_action_tuple(action)
                    self._partial_policy[next_state] = base
                    next_state = action_outcome.apply(next_state)
            else:
                print(self.determinizer.determinized_domain)
                print(result["stdout"])
                print(result["stderr"])
        base_action = self._partial_policy.get(state)
        # if not (self._expected_state and self._expected_state == state):
            # dproblem = self.determinizer(self.problem)
            # self.problem.init = state.to_initial_state()
            # result = self.planner(dproblem, timeout=remaining)
            # if result["plan-found"]:
                # self._last_plan = result["plan"]
                # self._last_plan.reverse()
            # else:
                # self._last_plan = None
                # self._expected_state = None
        # base_action = None
        # if self._last_plan:
            # next_action = self._last_plan.pop()
            # _, _, base_action = self.determinizer.process_action_tuple(next_action)
            # action_outcome = dproblem.domain.retrieve_action(*next_action)
            # self._expected_state = action_outcome.apply(dproblem.get_initial_state())
        return base_action

    def _reset(self):
        self._partial_policy = {}


class HindsightAgent(Agent):
   
    def __init__(self, problem, determinizer, planner, initial_calls=30,
            calls_per_pha=30, fail_cost=100, max_pha=100):
        self.problem = problem
        self.determinizer = determinizer 
        self.planner = planner
        self.initial_calls = initial_calls
        self.calls_per_pha = calls_per_pha
        self.fail_cost = fail_cost
        self.max_pha = max_pha
        self._aodeterminizer = AllOutcomeDeterminizer()
        self._aodeterminizer.set_domain(determinizer.original_domain)

    def _pha(self, state, remaining):
        pha = {}
        self.problem.init = state.to_initial_state()
        for idx in range(self.initial_calls):
            determinizer = self.determinizer if idx < self.initial_calls-1 else self._aodeterminizer
            dproblem = determinizer(self.problem)
            result = self.planner(dproblem, timeout=remaining/(self.initial_calls-idx))
            if result["plan-found"]:
                first_action = result["plan"][0]
                _, _, base_action = self.determinizer.process_action_tuple(first_action)
                base_action = self.problem.domain.retrieve_action(*base_action).tuple_representation()
                try:
                    pha[base_action].append(result["plan"])
                except KeyError:
                    pha[base_action] = [result["plan"]]
            remaining -= result["time-wall"]
            # print(idx)
        scored_pha = sorted([(len(plan), a) for a,plan in pha.items()], reverse=True)[:self.max_pha]
        print(scored_pha)
        return pha

    def _step(self, state, remaining):
        pass

    def _reset(self):
        pass

