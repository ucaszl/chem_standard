from collections import defaultdict

class SpeciesGraph:
    def __init__(self):
        self._out_edges = defaultdict(list)
        self._in_edges = defaultdict(list)

    def add_reaction(self, reaction):
        """
        Project a Reaction into species-level directed edges.
        """
        reactants = reaction.reactants
        products = reaction.products
        rid = reaction.canonical_key()

        for r in reactants:
            for p in products:
                src = r.formula
                dst = p.formula
                edge = {
                    "reaction": rid,
                    "from": src,
                    "to": dst,
                }
                self._out_edges[src].append(edge)
                self._in_edges[dst].append(edge)

    def successors(self, species):
        return self._out_edges.get(species, [])

    def predecessors(self, species):
        return self._in_edges.get(species, [])

    def species(self):
        return set(self._out_edges) | set(self._in_edges)
