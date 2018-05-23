import argparse
from ..parser import *
from ..determinization import *


def main(domainpath): #, problempath):
    with open(domainpath, "r") as f:
        text = f.read()
        tree = parse(text)
        domain = process_domain(tree)
    # with open(problempath, "r") as f:
        # text = f.read()
        # tree = parse(text)
        # problem = process_problem(tree, domain)
    # determinized = all_outcome_determinization(domain)
    # determinized = single_outcome_determinization(domain, "mlo")
    determinized = alpha_cost_likelihood_determinization(domain, 0.05, 1.0)
    print(determinized)
    # print(domain)
    # print(domain.actions[0])
    # expanded = expand_probabilistic_actions(domain.actions)
    # pdomain = remove_mdp_features(preprocess_domain(domain))
    # print(pdomain)
    # print(domain)
    # for a in expanded:
        # print(a)
    # for prob, e in expanded:
        # print("{} -> {}".format(prob, e))
    # print(problem)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domainpath", help="Filepath to LISP-like text file")
    # parser.add_argument("problempath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

