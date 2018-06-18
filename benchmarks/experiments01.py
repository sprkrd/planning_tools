#!/usr/bin/python3

import os
import re
import argparse
from tqdm import trange

import numpy as np

from planning_toolbox.parser import parse_file
from planning_toolbox.solvers import *
from planning_toolbox.determinization import *
from planning_toolbox.simulation import *
from planning_toolbox.agents import *


PROBLEM_FILE_RE = re.compile(r"p[0-9]+\.pddl")


AGENTS = {
        # "ao-ff": SimpleDeterminizerAgent(None, AllOutcomeDeterminizer(), FDPlanner(search="astar(cea())")),
        # "ml-ff": SimpleDeterminizerAgent(None, SingleOutcomeDeterminizer("mlo"), FDPlanner(search="astar(cea())")),
        # "ma-ff": SimpleDeterminizerAgent(None, SingleOutcomeDeterminizer("mae"), FDPlanner(search="astar(cea())")),

        "ao-ff": SimpleDeterminizerAgent(None, AllOutcomeDeterminizer(), FFPlanner(s=0)),
        "ml-ff": SimpleDeterminizerAgent(None, SingleOutcomeDeterminizer("mlo"), FFPlanner(s=0)),
        "ma-ff": SimpleDeterminizerAgent(None, SingleOutcomeDeterminizer("mae"), FFPlanner(s=0)),
        "alph-0.0": SimpleDeterminizerAgent(None, AlphaCostLikelihoodDeterminizer(0, 0, 3), FDPlanner(search="astar(cea(), max_time=30)")),
        "alph-0.1": SimpleDeterminizerAgent(None, AlphaCostLikelihoodDeterminizer(0.1, 0, 3), FDPlanner(search="astar(cea(), max_time=30)")),
        "alph-0.2": SimpleDeterminizerAgent(None, AlphaCostLikelihoodDeterminizer(0.2, 0, 3), FDPlanner(search="astar(cea(), max_time=30)")), 
        "alph-1.0": SimpleDeterminizerAgent(None, AlphaCostLikelihoodDeterminizer(1.0, 0, 3), FDPlanner(search="astar(cea(), max_time=30)")), 
        "ho-gl-15": HindsightAgent(None, HindsightDeterminizer("global", 15), FFPlanner(s=0), calls_per_pha=15, initial_calls=15, penalty=500),
        # "ho-gl-30": HindsightAgent(None, HindsightDeterminizer("global", 30), FFPlanner(s=0), calls_per_pha=30, initial_calls=30, penalty=500),
        "ho-lo-15": HindsightAgent(None, HindsightDeterminizer("local", 15), FFPlanner(s=0), calls_per_pha=15, initial_calls=15, penalty=500),
        # "ho-lo-30": HindsightAgent(None, HindsightDeterminizer("local", 30), FFPlanner(s=0), calls_per_pha=30, initial_calls=30, penalty=500),

        # "ho-gl-15": HindsightAgent(None, HindsightDeterminizer("global", 15), FDPlanner(search="astar(cea())"), calls_per_pha=15, initial_calls=15, penalty=500),
        # "ho-gl-30": HindsightAgent(None, HindsightDeterminizer("global", 30), FDPlanner(search="astar(cea())"), calls_per_pha=30, initial_calls=30, penalty=500),
        # "ho-lo-15": HindsightAgent(None, HindsightDeterminizer("local", 15), FDPlanner(search="astar(cea())"), calls_per_pha=15, initial_calls=15, penalty=500),
        # "ho-lo-30": HindsightAgent(None, HindsightDeterminizer("local", 30), FDPlanner(search="astar(cea())"), calls_per_pha=30, initial_calls=30, penalty=500),
}

HEADER1 = ["problem-idx", "trial", "timeout", "success", "elapsed(s)", "length", "reward"]
HEADER2 = ["Agent name", "Solved", "Solved (%)", "Timeout", "Timeout (%)", "Total",  "Avg. elapsed(s)", "Avg. length", "Avg. reward"]


def do_problem(idx, simulator, problem, agent, trials):
    agent.problem = problem.copy()
    results = []
    for trial in trange(trials, desc="trial"):
        simulator.reset()
        timeout, done, elapsed, step, state = agent(simulator, verbose=False)
        # timeout, done, elapsed, step, state = agent(simulator, verbose=True)
        results.append([idx, trial, int(timeout), int(done), elapsed, step, state.reward])
    return results


def get_summary(agname, rows):
    matrix = np.array(rows)
    solved = matrix[matrix[:,3]==1,:]
    timeout = matrix[matrix[:,2]==1,:]
    summary = [
            agname,
            solved.shape[0],
            100*solved.shape[0]/matrix.shape[0],
            timeout.shape[0],
            100*timeout.shape[0]/matrix.shape[0],
            matrix.shape[0],
            np.mean(solved[:,4]),
            np.mean(solved[:,5]),
            np.mean(solved[:,6]),
    ]
    return summary


def main(folder, number, trials, timeout):
    problem_name = folder.strip("/").split("/")[-1]
    # print(problem_name)
    domain = parse_file(os.path.join(folder, "domain.pddl"), "domain")
    problems = sorted(os.path.join(folder,f) for f in os.listdir(folder) if PROBLEM_FILE_RE.match(f))[:number]

    for agent in AGENTS.values():
        agent.determinizer.set_domain(domain)

    simulator = PpddlSimulator(timeout=timeout)

    results = {agname: [] for agname in AGENTS}

    for idx in trange(len(problems), desc="problem"):
        pfile = problems[idx]
        problem = parse_file(pfile, "problem", domain)
        simulator.reset(problem)
        agents = list(AGENTS.items())
        for jdx in trange(len(agents), desc="agent"):
            agname, agent = agents[jdx]
            results[agname] += do_problem(idx, simulator, problem, agent, trials)

    with open(problem_name + "-results-detailed.txt", "w") as f:
        for agname, rows in results.items():
            print(agname, file=f)
            print(",".join(HEADER1), file=f)
            for row in rows:
                print(",".join(map(str,row)), file=f)

    with open(problem_name + "-results-summary.txt", "w") as f:
        print(",".join(HEADER2), file=f)
        for agname, rows in results.items():
            s = get_summary(agname, rows)
            print(",".join(map(str,s)), file=f)

    # print(problem_name)
    # print(problems)

    # print(domain)
    # sdomain = parse_file(domainpath, "domain")
    # sproblem = parse_file(problempath, "problem", sdomain)
    # # determinizer = AllOutcomeDeterminizer()
    # # determinizer = AlphaCostLikelihoodDeterminizer(base=0, round_=2)
    # determinizer = HindsightDeterminizer("local", 15)
    # determinizer.set_domain(sdomain)
    # print(sdomain)
    # print(sproblem)

    # planner = FFPlanner(s=0)
    # # planner = FDPlanner(search="astar(cea())")
    # simulator = PpddlSimulator(sproblem)
    # # agent = SimpleDeterminizerAgent(sproblem.copy(), determinizer, planner)
    # agent = HindsightAgent(sproblem.copy(), determinizer, planner,
                # calls_per_pha=10, initial_calls=10, penalty=500)
    # # agent._pha(sproblem.get_initial_state(), 300)
    # agent(simulator, verbose=True)
    # print(agent.invokations)

PROBLEMS = [
        # "imagine_simple",
        # "ippc/ex-blocksworld",
        # "terrain",
        # "ippc/blocksworld",
        # "ippc/boxworld",
        # "ippc/rectangle-tireworld",
        # "ippc/schedule",
        # "ippc/sysadmin-ssp",
        "ippc/triangle-tireworld",
        # "ippc/zenotravel"
]

if __name__ == "__main__":
    # blocksworld  boxworld  ex-blocksworld  rectangle-tireworld  schedule  sysadmin-ssp  triangle-tireworld  zenotravel
    for problem in PROBLEMS:
        main(problem, 10, 10, 180)
    # parser = argparse.ArgumentParser()
    # parser.add_argument("folder")
    # parser.add_argument("number", type=int)
    # parser.add_argument("trials", type=int)
    # parser.add_argument("--timeout", type=int, default=300)
    # args = parser.parse_args()
    # main(**vars(args))

