from .graphs import Graph

from ..pddl import Predicate


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


class ImagineState:

    def __init__(self, predicates, objects=None):
        features = []
        self._untransformed_predicates = []
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
    def graph(self):
        return self._graph

    def remove_hidden(self):
        self._graph = Graph(*self._graph.features(ommit_hidden=True))

    def focus(self, obj, exclude_links=None, max_depth=1):
        exclude_links = exclude_links or ["partially-occludes"]
        self._graph = self._graph.subgraph(obj, exclude_links, max_depth)

