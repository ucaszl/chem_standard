from collections import defaultdict
from typing import Iterable, Set

from src.reaction import Reaction


class ReactionGraph:
    """
    Minimal reaction graph.

    - Nodes: Reaction (unique by identity / hash)
    - Index: species formula -> reactions involving that species
    """

    def __init__(self):
        self._reactions: Set[Reaction] = set()
        self._by_species = defaultdict(set)

    def add_reaction(self, r: Reaction):
        """
        Add a Reaction node to the graph.

        Duplicate reactions (same identity) are ignored automatically
        via Reaction.__hash__ / __eq__.
        """
        if r in self._reactions:
            return

        self._reactions.add(r)

        # index by species (reactants + products)
        for m in list(r.reactants) + list(r.products):
            self._by_species[m.formula].add(r)

    def add_reactions(self, reactions: Iterable[Reaction]):
        for r in reactions:
            self.add_reaction(r)

    def reactions_by_species(self, formula: str):
        """
        Return all reactions involving a given species formula.
        """
        return list(self._by_species.get(formula, []))

    def stats(self):
        """
        Basic graph statistics.
        """
        return {
            "reactions": len(self._reactions),
            "species": len(self._by_species),
        }
