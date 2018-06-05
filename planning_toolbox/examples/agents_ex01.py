import argparse
from ..parser import parse_file
from ..solvers import *
from ..determinization import *
from ..simulation import *
from ..agents import *


def main(filepath):
    sdomain, sproblem = parse_file(filepath, "both")
    # determinizer = AllOutcomeDeterminizer()
    determinizer = AlphaCostLikelihoodDeterminizer(round_=2)
    # determinizer = HindsightDeterminizer("global", 30)
    determinizer.set_domain(sdomain)
    print(sdomain)
    print(sproblem)

    planner = FFPlanner(s=5)
    simulator = PpddlSimulator(sproblem)
    agent = SimpleDeterminizerAgent(sproblem.copy(), determinizer, planner)
    agent(simulator, verbose=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("domainpath", help="Filepath to LISP-like text file")
    # parser.add_argument("problempath", help="Filepath to LISP-like text file")
    parser.add_argument("filepath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

