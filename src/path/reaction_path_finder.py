from collections import deque
from typing import List, Optional, Sequence

from src.graph.species_graph import SpeciesGraph
from src.rules.path_rule import PathRule


class ReactionPathFinder:
    def __init__(
        self,
        species_graph: SpeciesGraph,
        rules: Optional[Sequence[PathRule]] = None,
    ):
        self.graph = species_graph
        self.rules = list(rules) if rules is not None else []

    def _is_path_allowed(self, path: List[str]) -> bool:
        """
        Apply all rules to a candidate path.
        """
        for rule in self.rules:
            if not rule.is_path_allowed(path):
                return False
        return True

    def find_paths(
        self,
        start: str,
        target: str,
        max_depth: int = 5,
    ) -> List[List[str]]:
        """
        Breadth-first search on SpeciesGraph.

        Path format:
        [species, reaction, species, reaction, ..., species]
        """

        paths: List[List[str]] = []
        queue = deque()
        queue.append((start, [start]))

        while queue:
            current, path = queue.popleft()

            steps = (len(path) - 1) // 2
            if steps > max_depth:
                continue

            if current == target and steps > 0:
                paths.append(path)
                continue

            for edge in self.graph.out_edges(current):
                reaction = getattr(edge, "reaction", None)
                next_species = getattr(edge, "product", None)

                if next_species is None:
                    continue

                # depth must be checked BEFORE expansion
                next_steps = steps + 1
                if next_steps > max_depth:
                    continue

                new_path = path + [reaction, next_species]

                # unified rule gate
                if not self._is_path_allowed(new_path):
                    continue

                queue.append((next_species, new_path))

        return paths
