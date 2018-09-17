#!/usr/bin/python3

import sys
import os

# objects
PICKAXE = 0
CHARACTER = 1
BOULDER = 2
FLAG = 3
EMPTY = 4

# terrain types
LAND = 0
SHALLOW_SEA = 1
DEEP_SEA = 2

translations = {
        "c": (LAND, CHARACTER),
        "C": (LAND, CHARACTER),
        "p": (LAND, PICKAXE),
        "P": (LAND, PICKAXE),
        "B": (LAND, BOULDER),
        "B": (LAND, BOULDER),
        ".": (LAND, EMPTY),
        "x": (SHALLOW_SEA, EMPTY),
        "X": (DEEP_SEA, EMPTY),
        "o": (LAND, FLAG),
        "O": (LAND, FLAG),
}

terrain_lists = {
        LAND: [],
        SHALLOW_SEA: [],
        DEEP_SEA: [],
}

object_lists = {
        CHARACTER: [],
        BOULDER: [],
        PICKAXE: [],
        FLAG: [],
}


def tile_name(idx, jdx):
    return "x_{}_{}".format(idx,jdx)


def generate_connected_predicates(nrows, ncols):
    predicates = []
    for idx, jdx in ((idx,jdx) for idx in range(nrows) for jdx in range(ncols)):
        tile = tile_name(idx,jdx)
        if idx + 1 < nrows:
            tile_r1 = tile_name(idx+1, jdx)
            predicates.append(("(connected {} {})".format(tile, tile_r1)))
        if jdx + 1 < ncols:
            tile_c1 = tile_name(idx, jdx+1)
            predicates.append(("(connected {} {})".format(tile, tile_c1)))
    return predicates


def print_objects(l, type_, line_size=10):
    for idx, x in enumerate(l):
        if idx%line_size == 0: print("  ", end="")
        newline = idx%line_size == line_size-1 and idx != len(l)-1
        print(x, end="\n" if newline else " ")
    print(" - " + type_)


nrows = 0
ncols = 0

pfile = sys.argv[1]

pname = os.path.splitext(os.path.basename(pfile))[0]

mapfile = sys.argv[1]
with open(mapfile, "r") as f:
    for idx, row in enumerate(f):
        nrows += 1
        if not ncols: ncols = len(row)-1
        for jdx, tile in enumerate(row[:-1]):
            name = "x_{}_{}".format(idx, jdx)
            terrain, obj = translations[tile]
            terrain_lists[terrain].append(name)
            if obj != EMPTY:
                object_lists[obj].append(name)


sys.stdout = open(pname+".pddl", "w")

print("(define (problem {})".format(pname))
print("(:domain terrain)")

print("(:objects")
print_objects(terrain_lists[LAND], "land")
print_objects(terrain_lists[SHALLOW_SEA], "shallow-water")
print_objects(terrain_lists[DEEP_SEA], "deep-water")
print(")")
# print("  " + " ".join(terrain_lists[LAND]) + " - land")
# print("  " + " ".join(terrain_lists[SHALLOW_SEA]) + " - shallow-water")
# print("  " + " ".join(terrain_lists[DEEP_SEA]) + " - deep-water\n)")

init = ["(alive)"]
init += generate_connected_predicates(nrows, ncols)
init.append("(at {})".format(object_lists[CHARACTER][0]))
for x in object_lists[BOULDER]:
    init.append("(boulder-at {})".format(x))
for x in object_lists[PICKAXE]:
    init.append("(pickaxe-at {})".format(x))
for x in object_lists[FLAG]:
    init.append("(flag-at {})".format(x))
init.append("(= (reward) 0)")
print("(:init\n  " + "\n  ".join(init) + "\n)")
print("(:goal (goal-reached))")
print("(:metric maximize (reward))")
print(")")

