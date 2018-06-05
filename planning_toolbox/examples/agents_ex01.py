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
    determinizer = HindsightDeterminizer("local", 15)
    determinizer.set_domain(sdomain)
    print(sdomain)
    print(sproblem)

    # planner = FFPlanner(s=3,w=1)
    planner = FFPlanner(s=0)
    # planner = FDPlanner(search="astar(add())")
    simulator = PpddlSimulator(sproblem)
    # agent = SimpleDeterminizerAgent(sproblem.copy(), determinizer, planner)
    # agent(simulator, verbose=True)
    agent = HindsightAgent(sproblem.copy(), determinizer, planner)
    agent._pha(sproblem.get_initial_state(), 300)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("domainpath", help="Filepath to LISP-like text file")
    # parser.add_argument("problempath", help="Filepath to LISP-like text file")
    parser.add_argument("filepath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

