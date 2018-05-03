import argparse
from ..pddl import *


def main():
    e = ArithmeticQuery("+", Number(5),
            ArithmeticQuery("*", Number(7), Number(3)))
    comp = ComparisonQuery(">", e, Number(25))
    print(e)
    print(e.eval(None))
    print(comp)
    print(comp.eval(None))
    and_ = AndQuery(comp, NotQuery(ComparisonQuery("=", Number(1),
        Number(1))))
    print(and_)
    print(and_.eval(None))
    print(NotQuery(AtomicQuery(Predicate("empty"))))
    print(DeleteEffect(Predicate("empty")))

    print(TotalQuery([Object("?x", "block")], AtomicQuery(Predicate("clear", "x"))))
    print(TotalEffect([Object("?x", "block")], DeleteEffect(Predicate("clear", "x"))))
    # o = Object("?b0", "block")
    # p = Predicate("p")
    # print(p)
    # print(p.signature())
    # print(p.bind({"?x": "a", "?y": "b", "?z": "c"}))
    # print(p.is_ground())
    # print(o.bind({"?b0": "a"}))
    # print(o == "?b0")
    # print(hash(o))
    # print(hash("?b0"))


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("filepath", help="Filepath to LISP-like text file")
    # args = parser.parse_args()
    # main(**vars(args))
    main()

