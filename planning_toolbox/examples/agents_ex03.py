import argparse
from ..parser import parse_file
from ..solvers import *
from ..determinization import *
from ..simulation import *
from ..agents import *
from ..pddl import Problem


def main(serverdomain, clientdomain, serverproblem):
    server_domain = parse_file(serverdomain, "domain")
    client_domain = parse_file(clientdomain, "domain")
    server_problem = parse_file(serverproblem, "problem", server_domain)
    # determinizer = AllOutcomeDeterminizer()
    determinizer = AlphaCostLikelihoodDeterminizer(alpha=0, base=0, round_=2)
    # determinizer = HindsightDeterminizer("global", 15)
    determinizer.set_domain(client_domain)

    # planner = FFPlanner(s=0)
    planner = FDPlanner(search="astar(cea())")
    simulator = ImagineSimulator(PpddlSimulator(server_problem, timeout=180))
    agent = ImagineAgent(SimpleDeterminizerAgent(
        Problem(server_problem.name, client_domain), determinizer, planner))
    # agent = ImagineAgent(HindsightAgent(
        # Problem(server_problem.name, client_domain),
        # determinizer, planner, calls_per_pha=30, initial_calls=30, penalty=500))
    # agent._pha(sproblem.get_initial_state(), 300)
    agent(simulator, verbose=True)
    simulator.history[-1][1].graph.to_pdf("out/thing.pdf")
    # simulator.history[0][1].graph.to_pdf("out/initial-state-pdf")
    # for idx, (action, state) in enumerate(simulator.history[1:]):
        # name = "out/" + "{:02}-{}".format(idx+1, "_".join(action))
        # state.graph.to_pdf(name)
    # print(agent.invokations)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("serverdomain", help="Filepath to LISP-like text file")
    parser.add_argument("clientdomain", help="Filepath to LISP-like text file")
    parser.add_argument("serverproblem", help="Filepath to LISP-like text file")
    # parser.add_argument("filepath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

