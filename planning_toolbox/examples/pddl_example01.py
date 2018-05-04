import argparse
from ..pddl import *


def main():
    e = ArithmeticQuery("+", ConstantQuery(5),
            ArithmeticQuery("*", ConstantQuery(7), ConstantQuery(3)))
    print(e)
    print(e.eval(None))
    comp = ComparisonQuery(">", e, ConstantQuery(25))
    print(comp)
    print(comp.eval(None))
    and_ = AndQuery(comp, NotQuery(ComparisonQuery("=", ConstantQuery(1),
        ConstantQuery(2))))
    print(and_)
    print(and_.eval(None))
    print(NotQuery(PredicateQuery(AtomicFunctional("empty"))))
    print(DeleteEffect(AtomicFunctional("empty")))

    print(ExistentialQuery([Object("?x", "block")], PredicateQuery(AtomicFunctional("clear", "x"))))
    print(TotalEffect([Object("?x", "block")], DeleteEffect(AtomicFunctional("clear", "x"))))

    peff = ProbabilisticEffect(0.5, AddEffect(AtomicFunctional("empty")), 0.3,
        DeleteEffect(AtomicFunctional("clear", "?x")))

    for p, eff in peff:
        print(str(p) + " " + str(eff))

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

