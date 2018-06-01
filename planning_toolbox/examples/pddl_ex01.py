import argparse
from ..pddl import *


def main():
    requirements = [":strips", ":adl"]
    types = ["disk", "peg"]
    predicates = [
            Predicate("clear", ("?o", "object")),
            Predicate("on", ("?d", "disk"), ("?o", "object")),
            Predicate("smaller", ("?d", "disk"), ("?o", "object")),
    ]
    # actions = [
        # Action("move",
            # ObjectList(("?from", "object"), ("?to", "object"), ("?what", "disk")),
            # AndQuery(
                # PredicateQuery(Predicate("clear", "?to")),
                # PredicateQuery(Predicate("clear", "?what")),
                # PredicateQuery(Predicate("smaller", "?what", "?to")),
                # PredicateQuery(Predicate("on", "?what", "?from")),
            # ),
            # AndEffect(
                # AddEffect(Predicate("on", "?what", "?to")),
                # AddEffect(Predicate("clear", "?from")),
                # DeleteEffect(Predicate("on", "?what", "?from")),
                # DeleteEffect(Predicate("clear", "?to")),
                # AssignmentEffect("increase", Function("total-cost"), Constant(1))
            # )
        # )
    # ]
    actions = [
        Action("move",
            ObjectList(("?from", "object"), ("?to", "object"), ("?what", "disk")),
            AndQuery(
                ForallQuery(
                    ObjectList(("?d", "disk")),
                    AndQuery(
                        NotQuery(PredicateQuery(Predicate("on", "?d", "?what"))),
                        NotQuery(PredicateQuery(Predicate("on", "?d", "?to"))),
                    )
                ),
                PredicateQuery(Predicate("smaller", "?what", "?to")),
                PredicateQuery(Predicate("on", "?what", "?from")),
            ),
            AndEffect(
                AddEffect(Predicate("on", "?what", "?to")),
                DeleteEffect(Predicate("on", "?what", "?from")),
                AssignmentEffect("increase", Function("total-cost"), Constant(1))
            )
        )
    ]
    functions = [Function("total-cost")]

    objects = ObjectList(
            ("peg1", "peg"),
            ("peg2", "peg"),
            ("peg3", "peg"),
            ("d1", "disk"),
            ("d2", "disk"),
            ("d3", "disk")
    )
    init = InitialState([
        Predicate("smaller", "d1", "peg1"),
        Predicate("smaller", "d1", "peg2"),
        Predicate("smaller", "d1", "peg3"),
        Predicate("smaller", "d2", "peg1"),
        Predicate("smaller", "d2", "peg2"),
        Predicate("smaller", "d2", "peg3"),
        Predicate("smaller", "d3", "peg1"),
        Predicate("smaller", "d3", "peg2"),
        Predicate("smaller", "d3", "peg3"),
        Predicate("smaller", "d1", "d2"),
        Predicate("smaller", "d1", "d3"),
        Predicate("smaller", "d2", "d3"),
        Predicate("on", "d3", "peg1"),
        Predicate("on", "d2", "d3"),
        Predicate("on", "d1", "d2"),
        # Predicate("clear", "d1"),
        # Predicate("clear", "peg2"),
        # Predicate("clear", "peg3"),
    ], {
        Function("total-cost"): 0,
    })
    goal = Goal(AndQuery(
        PredicateQuery(Predicate("on", "d3", "peg3")),
        PredicateQuery(Predicate("on", "d2", "d3")),
        PredicateQuery(Predicate("on", "d1", "d2")),
    ), metric=("minimize", FunctionQuery(Function("total-cost")))
    )


    domain = Domain("hanoi", requirements, types, None, predicates, functions, actions)
    problem = Problem("hanoi-03", domain, objects, init, goal)

    print(domain)
    print(problem)

    s0 = problem.get_initial_state()
    print(s0)
    
    for a in s0.applicable_actions():
        print(a.short_str())
        s1 = a.apply(s0)
        print(s1)
    

    # print(" ".join(str(p) for p in domain.get_static_predicates()))
    # print(" ".join(str(p) for p in domain.get_static_functions()))

    # print(actions[0].bind({"?from": "a", "?to": "c", "?what": "b"}))

    # p = Predicate("on", ("?x", "block"), ("?y", "block"))
    # p = Predicate("empty-hand")
    # p = Function("on", ("?x", "block"))
    # q = Function("on", "?x")
    # print(hash(p))
    # print(hash(q))
    # print(p == q)
    # print(p.is_ground())
    # print(p)
    # print(Constant(6))
    # print(ForallQuery(ObjectList(("?x", "block")), Predicate("clean","?x")))
    # print(ProbabilisticEffect(
        # (0.3, AndEffect(AddEffect(Predicate("p", "?x")), AddEffect(Predicate("q", "?x", "?y")))),
        # (0.2, AddEffect(Predicate("q", "?y", "?x"))))
    # )
    # e = ArithmeticQuery("+", Constant(5),
            # ArithmeticQuery("*", Constant(7), Constant(3)))
    # print(e)
    # print(e.eval(None))

    # print(type_hierarchy_to_str(to_type_hierarchy(
        # {"block": None, "table": "furniture", "furniture": "thing", "couch": "furniture"})))
    # h = to_type_hierarchy({"block": "object", "table": "furniture", "furniture": "thing", "couch": "furniture"})
    # print(inferred_types(h, "table"))
    # print(e)
    # print(e.eval(None))
    # comp = ComparisonQuery(">", e, ConstantQuery(25))
    # print(comp)
    # print(comp.eval(None))
    # and_ = AndQuery(comp, NotQuery(ComparisonQuery("=", ConstantQuery(1),
        # ConstantQuery(2))))
    # print(and_)
    # print(and_.eval(None))
    # print(NotQuery(PredicateQuery(AtomicFunctional("empty"))))
    # print(DeleteEffect(AtomicFunctional("empty")))

    # print(ExistentialQuery([Object("?x", "block")], PredicateQuery(Predicate("clear", "x"))))
    # print(TotalEffect([Object("?x", "block")], DeleteEffect(Predicate("clear", "x"))))

    # peff = ProbabilisticEffect(0.5, AddEffect(AtomicFunctional("empty")), 0.3,
        # DeleteEffect(AtomicFunctional("clear", "?x")))

    # for p, eff in peff:
        # print(str(p) + " " + str(eff))

    # act = Action("pick", [Object("?b", "block")], AndQuery(
        # Predicate("on-table", "?b"), Predicate("clear", "?b"),
        # Predicate("empty-hand")), AndEffect(DeleteEffect(Predicate("empty-hand")),
            # AddEffect(Predicate("holding", "?b")), DeleteEffect(Predicate("clear", "?b"))))
    # print(act)

    # domain = Domain("test-domain", [":typing", ":adl"], {"block": "object"},
            # [Predicate("on", ("?x", "block"), ("?y", "block")),
             # Predicate("on-table", ("?x", "block")),
             # Predicate("clean", ("?x", "block"))], None, [act])
    # print(domain)

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

