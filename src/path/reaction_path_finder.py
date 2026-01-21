# src/path/reaction_path_finder.py
from collections import deque
from typing import List, Optional, Iterable, Any, Dict

from src.graph.species_graph import SpeciesGraph


class ReactionPathFinder:
    """
    ReactionPathFinder: BFS-based species-level path finder with rule injection.

    - species_graph: SpeciesGraph
    - reaction_rules: iterable of objects that implement either:
        - is_applicable(reaction) -> bool    (reaction-level)
        - or allow(path, reaction, graph) -> bool
        - optionally should_prune(path, reaction, graph) -> bool
    - path_rules: iterable of objects that implement either:
        - is_path_allowed(path) -> bool
        - or allow(path, reaction, graph) -> bool
        - optionally should_prune(path, reaction, graph) -> bool

    The finder will:
    1) For each candidate reaction edge, check reaction_rules to decide whether to consider it.
    2) Build a candidate new_path (list form).
    3) Ask path_rules (and reaction_rules with should_prune) whether to prune early.
    4) If allowed, enqueue for BFS.
    """

    def __init__(
        self,
        species_graph: SpeciesGraph,
        reaction_rules: Optional[Iterable[Any]] = None,
        path_rules: Optional[Iterable[Any]] = None,
        max_paths: int = 1000,
    ):
        self.graph = species_graph
        self.reaction_rules = list(reaction_rules) if reaction_rules else []
        self.path_rules = list(path_rules) if path_rules else []
        self.max_paths = int(max_paths)

        # statistics counters
        self._stats: Dict[str, int] = {
            "expanded": 0,
            "pruned_by_reaction_rule": 0,
            "pruned_by_path_rule": 0,
            "accepted": 0,
        }

    # ---- small adapters to support different rule interfaces ----
    def _reaction_allowed(self, path: List[str], reaction: Any) -> bool:
        """
        Return True if all reaction rules allow this reaction (conservative: all must allow).
        Accept different interfaces:
         - rule.is_applicable(reaction) -> bool
         - rule.allow(path, reaction, graph) -> bool
        """
        for r in self.reaction_rules:
            # prefer is_applicable if present
            if hasattr(r, "is_applicable"):
                try:
                    ok = bool(r.is_applicable(reaction))
                except Exception:
                    ok = False
            elif hasattr(r, "allow"):
                try:
                    ok = bool(r.allow(path, reaction, self.graph))
                except Exception:
                    ok = False
            else:
                # unknown rule interface -> conservatively allow
                ok = True

            if not ok:
                return False
        return True

    def _should_prune_by_reaction(self, path: List[str], reaction: Any) -> bool:
        """
        Return True if any reaction_rule requests pruning via should_prune.
        If none implement should_prune, return False.
        """
        pruned = False
        for r in self.reaction_rules:
            if hasattr(r, "should_prune"):
                try:
                    if bool(r.should_prune(path, reaction, self.graph)):
                        pruned = True
                        break
                except Exception:
                    # on exception be conservative and do not prune
                    continue
        return pruned

    def _path_allowed(self, new_path: List[str], reaction: Any) -> bool:
        """
        Return True if all path_rules allow the path.
        Path rule interfaces supported:
         - rule.is_path_allowed(path) -> bool
         - rule.allow(path, reaction, graph) -> bool
        """
        for r in self.path_rules:
            if hasattr(r, "is_path_allowed"):
                try:
                    ok = bool(r.is_path_allowed(new_path))
                except Exception:
                    ok = False
            elif hasattr(r, "allow"):
                try:
                    ok = bool(r.allow(new_path, reaction, self.graph))
                except Exception:
                    ok = False
            else:
                ok = True

            if not ok:
                return False
        return True

    def _should_prune_by_path(self, new_path: List[str], reaction: Any) -> bool:
        """
        Ask path_rules for should_prune. If none implement should_prune, returns False.
        """
        for r in self.path_rules:
            if hasattr(r, "should_prune"):
                try:
                    if bool(r.should_prune(new_path, reaction, self.graph)):
                        return True
                except Exception:
                    # conservative: do not prune on exceptions
                    continue
        return False

    # ---- public API ----
    def find_paths(self, start: str, target: str, max_depth: int = 5) -> List[List[str]]:
        """
        BFS find paths between species names.

        Path format: [species, reaction, species, reaction, ..., species]
        Steps = number of reactions = (len(path)-1)//2
        """
        self._stats = dict.fromkeys(self._stats.keys(), 0)

        results: List[List[str]] = []
        queue = deque()
        queue.append((start, [start]))

        while queue:
            current, path = queue.popleft()

            # pruning by depth
            steps = (len(path) - 1) // 2
            if steps > max_depth:
                continue

            # matched target (non-trivial path)
            if current == target and steps > 0:
                results.append(path)
                # optionally stop early if enough found
                if len(results) >= self.max_paths:
                    break
                # do not expand this target node further
                continue

            # expand outgoing edges
            for edge in self.graph.out_edges(current):
                self._stats["expanded"] += 1

                # edge may be SpeciesEdge or dict-like
                reaction = getattr(edge, "reaction", None) or edge.get("reaction") if isinstance(edge, dict) else None
                next_species = getattr(edge, "product", None) or edge.get("to") if isinstance(edge, dict) else None

                if next_species is None:
                    continue

                # reaction level pre-filter (is_applicable / allow)
                if not self._reaction_allowed(path, reaction):
                    self._stats["pruned_by_reaction_rule"] += 1
                    continue

                # optional reaction-level should_prune (early)
                if self._should_prune_by_reaction(path, reaction):
                    self._stats["pruned_by_reaction_rule"] += 1
                    continue

                new_path = path + [reaction, next_species]

                # path-level should_prune (early)
                if self._should_prune_by_path(new_path, reaction):
                    self._stats["pruned_by_path_rule"] += 1
                    continue

                # path-level allow / is_path_allowed
                if not self._path_allowed(new_path, reaction):
                    self._stats["pruned_by_path_rule"] += 1
                    continue

                # passed all checks -> accept
                self._stats["accepted"] += 1
                queue.append((next_species, new_path))

                # safety cap
                if len(results) >= self.max_paths:
                    break

        return results

    def stats(self) -> Dict[str, int]:
        """
        Return counters to inspect pruning effectiveness.
        """
        return dict(self._stats)
