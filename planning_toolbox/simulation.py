from time import time

class PpddlSimulator:

    def __init__(self, problem=None, timeout=180):
        self.timeout = timeout
        self.reset(problem)

    def reset(self, problem=None):
        if problem is not None:
            self.problem = problem
        self.current_state = self.problem.get_initial_state()

    def start(self):
        self.start_time = time()

    def elapsed(self):
        return time() - self.start_time

    def step(self, action):
        remaining = self.timeout - self.elapsed()
        done = False
        timeout = remaining <= 0
        if not timeout:
            grop = self.problem.domain.retrieve_action(*action)
            new_state = grop.apply(self.current_state)
            if new_state:
                done = self.problem.goal.query.eval(new_state)
                self.current_state = new_state
        return done, timeout, self.current_state

