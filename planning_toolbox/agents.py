
class Agent:
 
    def __call__(self, simulator, verbose=False):
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
            action = self._step(state)
            found = action is not None
            elapsed = simulator.elapsed()
            timestamp = "[{:.03f}s] ".format(simulator.elapsed())
            if found:
                step += 1
                done, timeout, state = simulator.step(action)
                if verbose:
                    print(timestamp + "State at step {}".format(step))
                    print(state)
        print(timestamp + "Stopped after {} step(s).".format(step), end=" ")
        if done: print("Success!".format(elapsed))
        elif timeout: print("Timeout!".format(elapsed))
        elif not found: print("Plan not found!")
        return timeout, done, elapsed, step, state

    def _step(self, state):
        raise NotImplementedError()


class SimpleDeterminizerAgent(Agent):

    def __init__(self, problem, determinizer, planner):
        self.problem = problem
        self.determinizer = determinizer 
        self.planner = planner

    def _step(self, state):
        self.problem.init = state.to_initial_state()
        dproblem = self.determinizer(self.problem)
        result = self.planner(dproblem)
        if result["plan-found"]:
            _, base_plan = self.determinizer.process_plan_trace(result["plan"])
            return base_plan[0]
        else:
            print(result["stderr"])
            print(result["stdout"])
            return None

