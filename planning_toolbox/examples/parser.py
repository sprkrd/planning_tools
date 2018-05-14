import argparse
from ..parser import *


def main(filepath):
    with open(filepath, "r") as f:
        text = f.read()
    tree = parse(text)
    print(treew
    d = w_domain(tree)
    print(d)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

