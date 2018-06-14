import argparse
from ..parser import parse_file
from ..solvers import *
from ..determinization import *
from ..simulation import *
from ..agents import *


def main(filepath):
    sdomain, sproblem = parse_file(filepath, "both")
    # determinizer = AllOutcomeDeterminizer()
    # determinizer = AlphaCostLikelihoodDeterminizer(base=0, round_=2)
    determinizer = HindsightDeterminizer("local", 30)
    determinizer.set_domain(sdomain)
    print(sdomain)
    print(sproblem)

    # planner = FFPlanner(s=0)
    planner = FDPlanner(search="astar(add())")
    simulator = PpddlSimulator(sproblem)
    # agent = SimpleDeterminizerAgent(sproblem.copy(), determinizer, planner)
    agent = HindsightAgent(sproblem.copy(), determinizer, planner,
                calls_per_pha=5, initial_calls=5)
    # agent._pha(sproblem.get_initial_state(), 300)
    agent(simulator, verbose=True)
    print(agent.invokations)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("domainpath", help="Filepath to LISP-like text file")
    # parser.add_argument("problempath", help="Filepath to LISP-like text file")
    parser.add_argument("filepath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

