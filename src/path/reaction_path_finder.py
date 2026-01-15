# src/path/reaction_path_finder.py
from collections import deque
from typing import List

from src.graph.species_graph import SpeciesGraph


class ReactionPathFinder:
    def __init__(self, graph: SpeciesGraph):
        self.graph = graph

    def find_paths(self, start: str, target: str, max_depth: int = 5) -> List[List[str]]:
        """
        Breadth-first search on SpeciesGraph.
        Each found path is a list: [species, reaction_id, species, reaction_id, ..., species]
        """

        paths = []
        queue = deque()
        # queue stores tuples: (current_species, path_list)
        queue.append((start, [start]))

        while queue:
            current, path = queue.popleft()

            # depth measured as number of reaction steps = (len(path)-1)//2
            steps = (len(path) - 1) // 2
            if steps > max_depth:
                continue

            if current == target and steps > 0:
                paths.append(path)
                # do not `continue` here: still allow exploring further paths of same length if desired
                # (but we don't expand the target node further to avoid cycles to itself)
                continue

            for edge in self.graph.out_edges(current):
                # defensive: allow edge being dict (legacy) or SpeciesEdge
                if isinstance(edge, dict):
                    next_species = edge.get("to") or edge.get("product")
                    reaction_id = edge.get("reaction") or edge.get("reaction_id")
                else:
                    next_species = getattr(edge, "product", None)
                    reaction_id = getattr(edge, "reaction_id", getattr(edge, "reaction", None))

                if next_species is None:
                    continue

                # avoid immediate cycles in path (simple check)
                if next_species in path:
                    continue

                new_path = path + [reaction_id, next_species]
                queue.append((next_species, new_path))

        return paths
