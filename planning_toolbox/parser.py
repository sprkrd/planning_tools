#!/usr/bin/python3

import re
import io


COMMENTS_RE = re.compile(";.*$", re.MULTILINE)
FRACTION_RE = re.compile("[0-9]+/[0-9]+")


class SyntaxTree:

    def __init__(self, node):
        if isinstance(node, (list, tuple)):
           assert all(isinstance(tree, SyntaxTree) for tree in node)
        self._node = node

    def is_atom(self):
        return not isinstance(self._node, (list, tuple))

    def is_symbol(self):
        return isinstance(self._node, str)

    def is_number(self):
        return isinstance(self._node, (int, float))

    def node(self):
        return self._node

    def _str_repr(self, output, prefix="", last=False):
        if self.is_atom():
            print(prefix + str(self._node), file=output)
        else:
            print(prefix + "[]", file=output)
            if prefix:
                nst_prefix = prefix[:-2]+(" " if last else "|") + " |_"
            else:
                nst_prefix = "|_"
            for idx, nst in enumerate(self):
                nst._str_repr(output, nst_prefix, idx==len(self)-1)

    def __iter__(self):
        assert not self.is_atom()
        return self._node.__iter__()

    def __len__(self):
        assert not self.is_atom()
        return len(self._node)

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

