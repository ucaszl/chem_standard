# src/graph/species_graph.py
from collections import defaultdict
from typing import Dict, List


class SpeciesEdge:
    """
    Directed species-level edge projected from a Reaction.
    Provides both `reaction` and `reaction_id` attributes for compatibility.
    """

    def __init__(self, reactant: str, product: str, reaction_key: str):
        self.reactant = reactant
        self.product = product
        # canonical id string for the reaction (primary storage)
        self.reaction_id = reaction_key
        # alias kept for historical compatibility (`reaction` used earlier)
        self.reaction = reaction_key

    def __repr__(self):
        return f"{self.reactant} -> {self.product} ({self.reaction_id})"


class SpeciesGraph:
    """
    Species-level directed graph.

    Nodes: species formula (str)
    Edges: SpeciesEdge
    """

    def __init__(self):
        self._out_edges: Dict[str, List[SpeciesEdge]] = defaultdict(list)
        self._in_edges: Dict[str, List[SpeciesEdge]] = defaultdict(list)

    # ---------- construction ----------

    def add_reaction(self, reaction):
        """
        Project a Reaction into species-level directed edges.
        """
        rid = reaction.canonical_key()

        for r in reaction.reactants:
            for p in reaction.products:
                edge = SpeciesEdge(
                    reactant=r.formula,
                    product=p.formula,
                    reaction_key=rid,
                )
                self._out_edges[r.formula].append(edge)
                self._in_edges[p.formula].append(edge)

    @classmethod
    def from_reaction_graph(cls, reaction_graph):
        g = cls()
        for r in reaction_graph.reactions():
            g.add_reaction(r)
        return g

    # ---------- public API ----------

    def out_edges(self, species: str):
        return list(self._out_edges.get(species, []))

    def in_edges(self, species: str):
        return list(self._in_edges.get(species, []))

    def successors(self, species: str):
        return self.out_edges(species)

    def predecessors(self, species: str):
        return self.in_edges(species)

    def species(self):
        return set(self._out_edges) | set(self._in_edges)
