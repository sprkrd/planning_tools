import argparse
from ..parser import parse_file
from ..solvers import *
from ..determinization import *
from ..simulation import *


def main(filepath):
    sdomain, sproblem = parse_file(filepath, "both")
    # determinizer = AllOutcomeDeterminizer()
    determinizer = AlphaCostLikelihoodDeterminizer(round_=2)
    # determinizer = HindsightDeterminizer("global", 30)
    determinizer.set_domain(sdomain)
    problem = determinizer(sproblem)
    print(problem.domain)
    print(problem)
    ##########
# def main(domainpath, problempath):
    # domain = parse_file(domainpath, "domain")
    # problem = parse_file(problempath, "problem", domain)
    # print(domain)
    # print(problem)

    done = False
    dead_end = False

    planner = FFPlanner(s=3, w=1)
    # planner = FFPlanner(s=5)
    # planner = FDPlanner(search="astar(add())")

    sim = PpddlSimulator(sproblem)
    
    while not done and not dead_end:
        result = planner(problem, timeout=None)
        print(result["plan-found"])
        if result["plan-found"]:
            print("Plan ({}):".format(len(result["plan"])))
            print("\n".join("(" + " ".join(t) + ")" for t in result["plan"]))
            print("Total cost: " + str(result["total-cost"]))
            print("Total elapsed: " + str(result["total-elapsed"]))
            p, base_plan = determinizer.process_plan_trace(result["plan"])
            print("%success: {}%".format(100*p))
            print("base plan: " + str(base_plan))
            done, _, next_state = sim.step(base_plan[0])
            next_state.total_cost = result["total-cost"]
            print(next_state)
            problem.init = next_state.to_initial_state()
        elif result["timeout"]:
            dead_end = True
            print("timeout")
        else:
            dead_end = True
            print(result["stdout"])
            print(result["stderr"])
        print(result["time-wall"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("domainpath", help="Filepath to LISP-like text file")
    # parser.add_argument("problempath", help="Filepath to LISP-like text file")
    parser.add_argument("filepath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

