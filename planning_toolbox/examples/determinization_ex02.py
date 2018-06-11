import argparse
from ..parser import parse_file
from ..determinization import *


def main(domainpath, problempath):
    domain = parse_file(domainpath, "domain")
    problem = parse_file(problempath, "problem", domain)
    determinizer = AllOutcomeDeterminizer()
    # print(domain)
    # print(problem)
    # determinizer = SingleOutcomeDeterminizer()
    determinizer = AlphaCostLikelihoodDeterminizer(alpha=0,base=0)
    # determinizer = HindsightDeterminizer("local", 10, True)
    determinizer.set_domain(domain)
    print(determinizer.original_domain, end="\n---\n")
    print(determinizer.preprocessed_domain, end="\n---\n")
    print(determinizer.determinized_domain)
    print(determinizer(problem))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domainpath", help="Filepath to LISP-like text file")
    parser.add_argument("problempath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

