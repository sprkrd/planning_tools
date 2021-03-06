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

    def __bool__(self):
        return bool(self.node)

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
    return pddl.ObjectList(*objects)


def process_functional(tree, predicate=True):
    if tree.is_symbol() and not predicate:
        name = tree.node
        objlist = pddl.ObjectList()
    else:
        name = tree[0].node
        objlist = process_objects(tree[1:])
    class_ = pddl.Predicate if predicate else pddl.Function
    return class_(name, objlist)


def process_functions(tree):
    functions = []
    is_type = False
    acc = []
    for e in tree[1:]:
        if is_type:
            for f in acc: f.type = e.node
            functions += acc
            acc = []
            is_type = False
        elif e.node == "-": is_type = True
        else: acc.append(process_functional(e, False))
    functions += acc
    return functions


def process_query(tree, domain):
    def is_predicate_symbol(tree):
        if tree[0].node == "=" and domain.allows_equality_predicate():
            ret = tree[1].is_symbol() and tree[2].is_symbol()
            ret = ret and tree[1].node not in (f.name for f in domain.functions)
            ret = ret and tree[2].node not in (f.name for f in domain.functions)
            return ret
        return tree[0].node in (p.name for p in domain.predicates)
    def is_function_symbol(tree):
        if tree[0].node == "reward" and domain.allows_reward_fluent():
            return True
        return tree[0].node in (f.name for f in domain.functions)
    query = None
    if not tree:
        query = pddl.EmptyQuery()
    elif tree.is_number():
        query = pddl.Constant(tree.node)
    elif is_predicate_symbol(tree):
        query = pddl.PredicateQuery(process_functional(tree))
    elif is_function_symbol(tree):
        query = pddl.FunctionQuery(process_functional(tree, False))
    elif tree[0].node in pddl.ArithmeticQuery.OPERATORS:
        lhs = process_query(tree[1], domain)
        rhs = process_query(tree[2], domain)
        query = pddl.ArithmeticQuery(tree[0].node, lhs, rhs)
    elif tree[0].node in pddl.ComparisonQuery.OPERATORS:
        lhs = process_query(tree[1], domain)
        rhs = process_query(tree[2], domain)
        query = pddl.ComparisonQuery(tree[0].node, lhs, rhs)
    elif tree[0].node == "and":
        query = pddl.AndQuery(*(process_query(e, domain) for e in tree[1:]))
    elif tree[0].node == "or":
        query = pddl.OrQuery(*(process_query(e, domain) for e in tree[1:]))
    elif tree[0].node == "not":
        query = pddl.NotQuery(process_query(tree[1], domain))
    elif tree[0].node == "imply":
        lhs = process_query(tree[1], domain)
        rhs = process_query(tree[2], domain)
        query = pddl.ImplyQuery(lhs, rhs)
    elif tree[0].node == "forall":
        params = process_objects(tree[1])
        innerq = process_query(tree[2], domain)
        query = pddl.ForallQuery(params, innerq)
    elif tree[0].node == "exists":
        params = process_objects(tree[1])
        innerq = process_query(tree[2], domain)
        query = pddl.ExistsQuery(params, innerq)
    else:
        raise Exception("Cannot process tree:\n" + str(tree))
    return query


def process_effect(tree, domain):
    effect = None
    if not tree:
        effect = pddl.EmptyEffect()
    elif tree[0].node in (p.name for p in domain.predicates):
        effect = pddl.AddEffect(process_functional(tree))
    elif tree[0].node == "not":
        effect = pddl.DeleteEffect(process_functional(tree[1]))
    elif tree[0].node == "and":
        effect = pddl.AndEffect(*(process_effect(e, domain) for e in tree[1:]))
    elif tree[0].node == "forall":
        params = process_objects(tree[1])
        innere = process_effect(tree[2], domain)
        effect = pddl.ForallEffect(params, innere)
    elif tree[0].node == "when":
        lhs = process_query(tree[1], domain)
        rhs = process_effect(tree[2], domain)
        effect = pddl.ConditionalEffect(lhs, rhs)
    elif tree[0].node in pddl.AssignmentEffect.OPERATORS:
        lhs = process_functional(tree[1], False)
        rhs = process_query(tree[2], domain)
        effect = pddl.AssignmentEffect(tree[0].node, lhs, rhs)
    elif tree[0].node == "probabilistic":
        effect = pddl.ProbabilisticEffect(*((p.node, process_effect(e, domain))
            for p, e in zip(tree[1::2], tree[2::2])))
    else:
        raise Exception("Cannot process tree:\n" + str(tree))
    return effect


def process_action(tree, domain):
    action = pddl.Action(tree[1].node)
    for kw, subtree in zip(tree[2::2], tree[3::2]):
        if kw.node == ":parameters":
            action.parameters = process_objects(subtree)
        elif kw.node == ":precondition":
            action.precondition = process_query(subtree, domain).simplify()
        elif kw.node == ":effect":
            action.effect = process_effect(subtree, domain).simplify()
    return action


def process_domain(tree):
    domain = pddl.Domain(tree[1][1].node)
    domain.requirements = [e.node for e in tree[2][1:]]
    for e in tree[3:]:
        if e[0].node == ":types":
            domain.type_hierarchy = process_types(e)
        elif e[0].node == ":constants":
            domain.constants = process_objects(e[1:])
        elif e[0].node == ":predicates":
            domain.predicates = [process_functional(p) for p in e[1:]]
        elif e[0].node == ":functions":
            domain.functions = process_functions(e)
        elif e[0].node == ":action":
            domain.actions.append(process_action(e, domain))
    return domain


def process_init(tree):
    init = pddl.InitialState()
    for e in tree:
        if e[0].node == "=":
            f = process_functional(e[1])
            init.functions[f] = e[2].node
        elif e[0].node == "probabilistic":
            plist = []
            for prob, elem in zip(e[1::2], e[2::2]):
                if elem[0].node == "and":
                    plist.append((prob.node, [process_functional(p) for p in elem[1:]]))
                else:
                    plist.append((prob.node, process_functional(elem)))
            init.probabilistic.append(plist)
        else:
            init.predicates.append(process_functional(e))
    return init


def process_problem(tree, domain):
    problem = pddl.Problem(tree[1][1].node, domain)
    for e in tree[3:]:
        if e[0].node == ":objects":
            problem.objects = process_objects(e[1:])
        elif e[0].node == ":init":
            problem.init = process_init(e[1:])
        elif e[0].node == ":goal":
            problem.goal.query = process_query(e[1], domain)
        elif e[0].node == ":goal-reward":
            problem.goal.reward = e[1].node
        elif e[0].node == ":metric":
            problem.goal.metric = (e[1].node, process_query(e[2], domain))
    return problem


def parse(text, type_="domain", domain=None):
    assert type_ in ("raw", "domain", "problem", "both")
    text_wo_comments = remove_comments(text.lower())
    tokens = tokenize(text_wo_comments)
    tokens.reverse()
    if type_ == "raw":
        return read_from_tokens(tokens)
    elif type_ == "domain":
        return process_domain(read_from_tokens(tokens))
    elif type_ == "problem":
        return process_problem(read_from_tokens(tokens), domain)
    else: # type_ == both
        domain = process_domain(read_from_tokens(tokens))
        problem = process_problem(read_from_tokens(tokens), domain)
        return domain, problem


def parse_file(filename, type_="domain", domain=None):
    with open(filename,"r") as f:
        text = f.read()
    return parse(text, type_, domain)

