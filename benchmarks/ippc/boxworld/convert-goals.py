#!/usr/bin/python3

import os
import re
from planning_toolbox.pddl import *
from planning_toolbox.parser import parse_file

domain = parse_file("./old/domain.pddl", "domain")

all_problems = [f for f in os.listdir("./old") if f.startswith("p") and f.endswith(".pddl")]

for f in all_problems:
    problem = parse_file("./old/"+f, "problem", domain)
    boxes = problem.all_objects_of_type("box")
    destinations = {}
    predicates = []
    for p in problem.init.predicates:
        if p.name == "destination":
            destinations[p.arguments[0].name] = p.arguments[1].name
        else:
            predicates.append(p)
    problem.init.predicates = predicates
    problem.goal.query = AndQuery(*(Predicate("box-at-city", k, v) for k, v in destinations.items()))
    with open(f, "w") as f:
        f.write(str(problem))

