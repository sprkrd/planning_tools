import graphviz as gv
import os

def nice_html_list(labels):
    if labels:
        return "<br/>".join("<i>"+l+"</i>" for l in sorted(labels))
    return ""


def refactor_edge_dict(edge_dict):
    refactored = {}
    for from_, out in edge_dict.items():
        for to, label in out:
            try:
                refactored[(from_,to)].append(label)
            except KeyError:
                refactored[(from_,to)] = [label]
    return refactored


def inverse_edge_dict(edge_dict):
    inverse = {}
    for from_, out in edge_dict.items():
        for to, label in out:
            try:
                inverse[to].append((from_,label))
            except KeyError:
                inverse[to] = [(from_,label)]
    return inverse


def bfs(focus, E, exclude_links, max_depth):
    E_inverse = inverse_edge_dict(E)
    reached = set((focus,))
    queue = [(0,focus)]
    while queue:
        depth, front = queue.pop(0)
        if depth < max_depth:
            neighbors = E.get(front,[]) + E_inverse.get(front,[])
            for adj, label in neighbors:
                if adj not in reached and label not in exclude_links:
                    reached.add(adj)
                    queue.append((depth+1,adj))
    return reached


class Graph:
    def __init__(self, *args):
        self._V = {}
        self._E = {}
        self._hidden = set()
        self._occluded = set()
        for arg in args:
            if len(arg) == 2:
                try:
                    self.V[arg[0]].append(arg[1])
                except KeyError:
                    self.V[arg[0]] = [arg[1]]
            else: # assume len(arg) = 3
                if arg[2] in ("hides-component", "hides-affordance"):
                    self._hidden.add(arg[1])
                elif arg[2] == "partially-occludes":
                    self._occluded.add(arg[1])
                try:
                    self.E[arg[0]].append(arg[1:])
                except KeyError:
                    self.E[arg[0]] = [arg[1:]]

    @property
    def V(self):
        return self._V

    @property
    def E(self):
        return self._E

    @property
    def hidden(self):
        return self._hidden

    @property
    def occluded(self):
        return self._occluded

    def features(self, ommit_hidden=False):
        for vertex, labels in self.V.items():
            if not ommit_hidden or vertex not in self.hidden:
                for label in labels:
                    yield (vertex, label)
        for from_, out in self.E.items():
            if not ommit_hidden or from_ not in self.hidden:
                for to, label in out:
                    if not ommit_hidden or to not in self.hidden:
                        yield (from_, to, label)

    def ommit_occluded(self):
        features = []
        for vertex, labels in self.V.items():
            if vertex not in self.occluded:
                for label in labels:
                    features.append((vertex, label))
        for from_, out in self.E.items():
            if from_ not in self.occluded:
                for to, label in out:
                    if to not in self.occluded:
                        features.append((from_, to, label))
        return Graph(*features)

    def subgraph(self, focus, exclude_links=None, max_depth=1):
        exclude_links = exclude_links or []
        reached = bfs(focus, self.E, exclude_links, max_depth)
        features = []
        for vertex in reached:
            for label in self.V[vertex]:
                features.append((vertex,label))
            for to, label in self.E.get(vertex, []):
                if label not in exclude_links and to in reached:
                    features.append((vertex,to,label))
        return Graph(*features)

    def _dot_(self): 
        gv_graph = gv.Digraph()
        for vertex, labels in self.V.items():
            hidden = vertex in self.hidden
            style = "filled" if hidden else None
            color = "#cccccc" if hidden else None
            gv_graph.node(str(vertex), label="<<b>{}</b>{}>".format(
                vertex, ("<br/>"+nice_html_list(labels)) if labels else ""),
                style=style, fillcolor=color)
        for (from_, to), labels in refactor_edge_dict(self.E).items():
            hidden = from_ in self.hidden or to in self.hidden
            style = "dashed" if hidden else None
            gv_graph.edge(str(from_), str(to),
                    "<"+nice_html_list(labels)+">", style=style)
        gv_graph.node_attr["shape"] = "box"
        # gv_graph.graph_attr["rankdir"] = "LR"
        return gv_graph

    def to_pdf(self, filename):
        self._dot_().render(filename, view=False)
        os.system("pdfcrop "+filename+".pdf")

    def _repr_svg_(self):
        dot = self._dot_()
        return dot._repr_svg_()

    def __str__(self):
        return str(self.features)


