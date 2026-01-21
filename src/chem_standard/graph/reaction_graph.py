from collections import defaultdict
from typing import Iterable, Set, List

from chem_standard.reaction import Reaction
from chem_standard.dataset.reaction_dataset import ReactionDataset


class ReactionGraph:
    """
    Minimal reaction graph.

    - Nodes: Reaction (unique by identity / hash)
    - Index: species formula -> reactions involving that species
    """

    def __init__(self):
        self._reactions: Set[Reaction] = set()
        self._by_species = defaultdict(set)

    # ---------- construction ----------

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

    @classmethod
    def from_dataset(cls, ds: ReactionDataset) -> "ReactionGraph":
        """
        Build a ReactionGraph from a ReactionDataset.
        """
        g = cls()
        g.add_reactions(ds.reactions())
        return g

    # ---------- public query API ----------

    def reactions(self) -> List[Reaction]:
        """
        Return all reactions in the graph.

        This is the ONLY supported way to iterate over reactions.
        """
        return list(self._reactions)

    def reactions_by_species(self, formula: str) -> List[Reaction]:
        """
        Return all reactions involving a given species formula.
        """
        return list(self._by_species.get(formula, []))

    def species(self):
        """
        Return all species formulas appearing in the graph.
        """
        return set(self._by_species.keys())

    # ---------- diagnostics ----------

    def stats(self):
        """
        Basic graph statistics.
        """
        return {
            "reactions": len(self._reactions),
            "species": len(self._by_species),
        }

