from time import time

from .imagine.imagine_state import ImagineState

class PpddlSimulator:

    def __init__(self, problem=None, timeout=180):
        self.timeout = timeout
        self.problem = problem
        self.reset(problem)

    def reset(self, problem=None):
        if problem is not None:
            self.problem = problem
        if self.problem is not None:
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


class ImagineSimulator:

    def __init__(self, simulator):
        self.simulator = simulator
        self.history = []

    def reset(self, problem=None):
        self.simulator.reset(problem)
        self.history = [(None, self._current_state(ommit_hidden=False))]

    def _current_state(self, ommit_hidden=True):
        state = ImagineState(self.simulator.current_state.predicates,
                objects=self.simulator.problem.objects)
        if ommit_hidden: state.remove_hidden()
        state.reward = self.simulator.current_state.reward
        return state

    @property
    def current_state(self):
        return self._current_state()

    @property
    def timeout(self):
        return self.simulator.timeout

    def start(self):
        self.simulator.start()

    def elapsed(self):
        return self.simulator.elapsed()

    def step(self, action):
        done, timeout, _ = self.simulator.step(action)
        state = self._current_state(ommit_hidden=False)
        self.history.append((action, state))
        return done, timeout, self.current_state


