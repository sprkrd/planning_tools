
class PpddlSimulator:

    def __init__(self, problem=None):
        self.reset(problem)

    def reset(self, problem=None):
        if problem is not None:
            self.problem = problem
        self.current_state = problem.get_initial_state()

    def step(self, action):
        grop = self.problem.domain.retrieve_action(*action)
        new_state = grop.apply(self.current_state)
        if new_state:
            done = self.problem.goal.query.eval(new_state)
            self.current_state = new_state
        else:
            # done = False
            raise Exception("Invalid action")
        return done, self.current_state

