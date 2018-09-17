#!/usr/bin/env python3

import argparse
from planning_toolbox.parser import parse_file
from planning_toolbox.determinization import *


def main(filepath):
    # domain, problem = parse_file(filepath, "both")
    domain = parse_file(filepath, "domain")
    # determinizer = AllOutcomeDeterminizer()
    # determinizer = SingleOutcomeDeterminizer()
    determinizer = AlphaCostLikelihoodDeterminizer(alpha=1)
    # determinizer = HindsightDeterminizer("local", 10, True)
    determinizer.set_domain(domain)
    # print(determinizer.original_domain, end="\n---\n")
    # print(determinizer.preprocessed_domain, end="\n---\n")
    # print(determinizer.determinized_domain)
    ddomain = determinizer.determinized_domain
    print(ddomain)
    cost_effects = ddomain.get_total_cost_increase()
    for eff in cost_effects:
        print(eff)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

