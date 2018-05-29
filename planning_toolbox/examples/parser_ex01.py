import argparse
from ..parser import *


def main(filepath, process):
    if process == "both":
        domain, problem = parse_file(filepath, process)
        print(domain)
        print(problem)
    else:
        obj = parse_file(filepath, process)
        print(obj)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="Filepath to LISP-like text file")
    parser.add_argument("--process", choices=["raw","domain","problem","both"],
            help="Select the processor to be applied", default="raw")
    args = parser.parse_args()
    main(**vars(args))

