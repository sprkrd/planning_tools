import argparse
from ..parser import parse, print_syntax_tree


def main(filepath):
    with open(filepath, "r") as f:
        text = f.read()
    tree = parse(text)
    print(tree)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Filepath to LISP-like text file")
    args = parser.parse_args()
    main(**vars(args))

