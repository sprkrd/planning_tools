import argparse
from ..parser import *


def main(domainpath, problempath):
    with open(domainpath, "r") as f:
        text = f.read()
        tree = parse(text)
        domain = process_domain(tree)
    with open(problempath, "r") as f:
        text = f.read()
        tree = parse(text)
        problem = process_problem(tree, domain)
    print(domain)
    print(problem)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domainpath", help="Filepath to LISP-like text file")
    parser.add_argument("problempath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

