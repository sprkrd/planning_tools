import argparse
from ..parser import parse_file
from ..solvers import *
from ..determinization import *
from ..simulation import *


def main(filepath):
    sdomain, sproblem = parse_file(filepath, "both")
    # determinizer = AllOutcomeDeterminizer()
    determinizer = AlphaCostLikelihoodDeterminizer(alpha=1, round_=2)
    # determinizer = HindsightDeterminizer("global", 20, False)
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

    # planner = FFPlanner(s=0)
    planner = FDPlanner(search="astar(add())")
    result = planner(problem, timeout=None)
    print("Plan found!" if result["plan-found"] else "Plan not found")
    if result["plan-found"]:
        print("Plan ({}):".format(len(result["plan"])))
        print("\n".join("(" + " ".join(t) + ")" for t in result["plan"]))
        print("Total cost: " + str(result["total-cost"]))
        print("Total elapsed: " + str(result["total-elapsed"]))
        p, base_plan = determinizer.process_plan_trace(result["plan"])
        print("%success: {}%".format(100*p))
        print("base plan: " + str(base_plan))
    elif result["timeout"]:
        print("timeout")
    else:
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

