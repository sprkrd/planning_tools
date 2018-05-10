#!/usr/bin/python3

import re
import io

from . import pddl


COMMENTS_RE = re.compile(";.*$", re.MULTILINE)
FRACTION_RE = re.compile("[0-9]+/[0-9]+")


class SyntaxTree:

    def __init__(self, node):
        if isinstance(node, (list, tuple)):
           assert all(isinstance(tree, SyntaxTree) for tree in node)
        self.node = node

    def is_atom(self):
        return not isinstance(self.node, (list, tuple))

    def is_symbol(self):
        return isinstance(self.node, str)

    def is_number(self):
        return isinstance(self.node, (int, float))

    def _str_repr(self, output, prefix="", last=False):
        if self.is_atom():
            print(prefix + str(self.node), file=output)
        else:
            print(prefix + "[]", file=output)
            if prefix:
                nst_prefix = prefix[:-2]+(" " if last else "|") + " |_"
            else:
                nst_prefix = "|_"
            for idx, nst in enumerate(self):
                nst._str_repr(output, nst_prefix, idx==len(self)-1)

    def __iter__(self):
        return self.node.__iter__()

    def __len__(self):
        return len(self.node)

    def __getitem__(self, val):
        return SyntaxTree(self.node[val]) if isinstance(val, slice) else self.node[val]

    def __str__(self):
        output = io.StringIO()
        self._str_repr(output)
        return output.getvalue()


def remove_comments(text):
    """ Remove all the LISP-style comments (i.e. all the characters preceded by a
    semicolon until the line break) """
    return COMMENTS_RE.sub("", text)


def tokenize(text):
    """ Returns a list with tokens """
    return text.replace("(", " ( ").replace(")", " ) ").split()


def atom(token):
    try: return SyntaxTree(int(token))
    except ValueError: pass
    if FRACTION_RE.match(token): return SyntaxTree(eval(token))
    try: return SyntaxTree(float(token))
    except ValueError: pass
    return SyntaxTree(token)


def read_from_tokens(tokens):
    if not tokens:
        raise SyntaxError("unexpected EOF")
    token = tokens.pop()
    if token == "(":
        L = []
        while tokens[-1] != ")":
            L.append(read_from_tokens(tokens))
        tokens.pop() # pop off ")"
        return SyntaxTree(L)
    elif token == ")":
        raise SyntaxError("unexpected )")
    return atom(token)


def parse(text):
    text_wo_comments = remove_comments(text)
    tokens = tokenize(text_wo_comments)
    tokens.reverse()
    syntax_tree = read_from_tokens(tokens)
    return syntax_tree


def process_types(tree):
    hierarchy = {}
    acc = []
    is_parent = False
    for e in tree[1:]:
        if is_parent:
            for t in acc: hierarchy[t] = e.node
            is_parent = False
            del acc[:]
        elif e.node == "-": is_parent = True
        else: acc.append(e.node)
    for t in acc: hierarchy[t] = None
    return pddl.to_type_hierarchy(hierarchy)


def process_objects(tree):
    objects = []
    acc = []
    is_type = False
    for e in tree:
        if is_type:
            objects += [(o, e.node) for o in acc]
            is_type = False
            acc = []
        elif e.node == "-": is_type = True
        else: acc.append(e.node)
    objects += acc
    return objects


def process_predicate(tree):
    name = tree[0].node
    args = process_objects(tree[1:])
    return pddl.Predicate(name, *args)


def process_functions(tree):
    is_type = False
    for e in tree:
        if is_type:
            pass



def process_domain(tree):
    domain = pddl.Domain(tree[1][1])
    domain.name = tree[1][1].node
    domain.requirements = [e.node for e in tree[2][1:]]
    for e in tree[3:]:
        if e[0].node == ":types":
            domain.type_hierarchy = process_types(e)
        elif e[0].node == ":predicates":
            domain.predicates = [process_predicate(p) for p in e[1:]]
        elif e[0].node == ":functions":
            raise NotImplementedError(i)
        elif e[0].node == ":action":
            pass
    return domain


def print_syntax_tree(tree, prefix="", last=False):
    if isinstance(tree, list):
        print(prefix + "[]")
        if prefix:
            nst_prefix = prefix[:-2]+(" " if last else "|") + " |_"
        else:
            nst_prefix = "|_"
        for idx, nst in enumerate(tree):
            print_syntax_tree(nst, nst_prefix, idx==len(tree)-1)
    else:
        print(prefix + str(tree))

