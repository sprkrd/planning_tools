#!/usr/bin/python3

import re


COMMENTS_RE = re.compile(";.*$", re.MULTILINE)
FRACTION_RE = re.compile("[0-9]+/[0-9]+")


def remove_comments(text):
    """ Remove all the LISP-style comments (i.e. all the characters preceded by a
    semicolon until the line break) """
    return COMMENTS_RE.sub("", text)


def tokenize(text):
    """ Returns a list with tokens """
    return text.replace("(", " ( ").replace(")", " ) ").split()


def atom(token):
    try: return int(token)
    except ValueError: pass
    if FRACTION_RE.match(token): return eval(token)
    try: return float(token)
    except ValueError: pass
    return token


def read_from_tokens(tokens):
    if not tokens:
        raise SyntaxError("unexpected EOF")
    token = tokens.pop()
    if token == "(":
        L = []
        while tokens[-1] != ")":
            L.append(read_from_tokens(tokens))
        tokens.pop() # pop off ")"
        return L
    elif token == ")":
        raise SyntaxError("unexpected )")
    return atom(token)


def parse(text):
    text_wo_comments = remove_comments(text)
    tokens = tokenize(text_wo_comments)
    tokens.reverse()
    syntax_tree = read_from_tokens(tokens)
    return syntax_tree


def print_syntax_tree(tree, prefix=""):
    if not isinstance(tree, list):
        # the top level may contain a single atom (not-a-list)
        print("{}{}".format(prefix, tree))
    else:
        nst_prefix = prefix[:-2] + ("| |_")
        nst_prefix_last = prefix[:-2] + ("  |_")
        for idx, elem in enumerate(tree):
            if isinstance(elem, list):
                print("|_" if not prefix else prefix)
                last = idx == len(tree) - 1
                print_syntax_tree(elem, nst_prefix_last if last else nst_prefix)
            else:
                print("{}{}".format(prefix, elem))


if __name__ == "__main__":
    # with open("ex-blocksworld/p01-n2-N5-s1.pddl", "r") as f:
    with open("ex-blocksworld/domain.pddl", "r") as f:
        d = f.read()
    # print(d)
    # print(remove_comments(d))
    # print(tokenize(remove_comments(d)))
    tree = parse(d)
    print_syntax_tree(tree)

