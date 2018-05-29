import argparse
from ..parser import parse_file
from ..determinization import *


def main(filepath):
    domain, problem = parse_file(filepath, "both")
    # determinizer = AllOutcomeDeterminizer()
    # determinizer = SingleOutcomeDeterminizer()
    determinizer = AlphaCostLikelihoodDeterminizer()
    determinizer.set_domain(domain)
    print(determinizer.original_domain, end="\n---\n")
    print(determinizer.preprocessed_domain, end="\n---\n")
    print(determinizer.determinized_domain)
    print(determinizer(problem))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

