#!/usr/bin/python3

import sys

# objects
PICKAXE = "\u26CF "
CHARACTER = "\u263A "
BOULDER = "\u26f0 "
FLAG = "\U0001f6a9 "
EMPTY = "  "

# terrain types
LAND = "\033[42m"
SHALLOW_SEA = "\033[46m"
DEEP_SEA = "\033[44m"
NONE = "\033[49m"

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

# reset all attributes
RESET = "\033[0m"

current_terrain = NONE

def print_terrain(terrain_type=LAND, obj=EMPTY, eol=False):
    global current_terrain
    if current_terrain != terrain_type:
        print(terrain_type, end="")
        current_terrain = terrain_type
    print(obj, end="\n" if eol else "")

def reset():
    print(RESET, end="") 

print("\033[30m", end="")

try:
    mapfile = sys.argv[1]
    with open(mapfile, "r") as f:
        for row in f:
            for tile in row[:-2]:
                print_terrain(*translations[tile])
            print_terrain(*translations[row[-2]], True)
finally:
    reset()

