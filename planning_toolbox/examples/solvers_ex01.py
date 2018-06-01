import argparse
from ..parser import parse_file
from ..solvers import *
from ..determinization import *


def main(domainpath, problempath, planner, time_out):
    domain = parse_file(domainpath, "domain")
    problem = parse_file(problempath, "problem", domain)
    print(domain)
    print(problem)
    planner = FFPlanner(s=0) if planner == "ff" else FDPlanner(search="astar(add())")
    result = planner(problem, timeout=time_out)
    print("Plan found!" if result["plan-found"] else "Plan not found")
    if result["plan-found"]:
        print("Plan ({}):".format(len(result["plan"])))
        print("\n".join("\t(" + " ".join(t) + ")" for t in result["plan"]))
        print("Total cost: " + str(result["total-cost"]))
        print("Total elapsed: " + str(result["total-elapsed"]))
    elif result["timeout"]:
        print("timeout")
    else:
        print(result["stdout"])
        print(result["stderr"])
    print("wall time: {}s".format(result["time-wall"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domainpath", help="Filepath to LISP-like text file")
    parser.add_argument("problempath", help="Filepath to LISP-like text file")
    parser.add_argument("-t", "--time-out", help="Time before aborting")
    parser.add_argument("-p", "--planner", help="Planner name", choices=["ff", "fd"],
            default="ff")
    args = parser.parse_args()
    print(args)
    main(**vars(args))

