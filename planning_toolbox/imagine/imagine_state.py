import re

from .graphs import Graph

from ..pddl import Predicate, ObjectList


RE_FUNCTIONAL_FEATURE = re.compile(r"([a-z0-9\-]+)\(([a-z0-9\-]+)\)")


def transform_to_feature(predicate):
    if predicate.name in ("has-affordance", "fixed-by", "connected",
            "hides-component", "hides-affordance", "partially-occludes"):
        return (predicate.arguments[0].name, predicate.arguments[1].name, predicate.name)
    if predicate.name in ("has-confidence", "at-side", "valid-sd"):
        return (predicate.arguments[0].name, "{}({})".format(
            predicate.name, predicate.arguments[1].name))
    if predicate.name in ("broken-component", "clear", "removed-verified",
            "removed-non-verified", "stuck", "loose"):
        return (predicate.arguments[0].name, predicate.name)
    return None


def transform_to_predicate(feature):
    if len(feature) == 3:
        return Predicate(feature[2], feature[0], feature[1])
    m = RE_FUNCTIONAL_FEATURE.match(feature[1])
    if m:
        return Predicate(m.group(1), feature[0], m.group(2))
    if feature[1] in ("broken-component", "clear", "removed-verified",
            "removed-non-verified", "stuck", "loose"):
        return Predicate(feature[1], feature[0])
    return None


class ImagineState:

    def __init__(self, predicates, objects=None):
        features = []
        self._untransformed_predicates = []
        self._objects = objects
        if objects:
            for o in objects:
                if o.type not in ("side", "affordance-confidence", "mode",
                        "screwdriver", "tool"):
                    features.append((o.name, o.type))
        for p in predicates:
            f = transform_to_feature(p)
            if f is None:
                self._untransformed_predicates.append(p)
            else:
                features.append(f)
        self._graph = Graph(*features)

    @property
    def predicates(self):
        predicates = []
        for f in self.graph.features():
            p = transform_to_predicate(f)
            if p: predicates.append(p)
        predicates += self._untransformed_predicates
        return predicates

    @property
    def objects(self):
        return self._objects

    @property
    def graph(self):
        return self._graph

    def remove_hidden(self):
        self._graph = Graph(*self._graph.features(ommit_hidden=True))

    def remove_occluded(self):
        self._graph = self._graph.ommit_occluded()

    def focus(self, obj, exclude_links=None, max_depth=1):
        exclude_links = exclude_links or ["partially-occludes"]
        self._graph = self._graph.subgraph(obj, exclude_links, max_depth)
        self._objects = ObjectList(*(obj for obj in self._objects if obj.name in self._graph.V))
        # print(list(map(str,self._objects)))


