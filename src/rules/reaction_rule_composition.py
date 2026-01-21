# src/rules/reaction_rule_composition.py
"""
Minimal CompositeRule + DepthLimitRule for P4-3 (safe, minimal).
Designed to work with existing ReactionPathFinder which expects rules
implementing `allow(path, candidate_reaction, graph)` and optional `should_prune`.
"""

from typing import Sequence, Iterable, Optional
from chem_standard.rules.path_rule import PathRule
from typing import List, Any

# 灏濊瘯瀵煎叆浠撳簱鍐呯殑 ReactionRule锛堣嫢瀛樺湪锛?
try:
    from chem_standard.rules.reaction_rule import ReactionRule  # type: ignore
except Exception:
    # 绠€鍗曞洖閫€鍩虹被锛堜粎绾﹀畾鎺ュ彛锛?
    class ReactionRule:
        def allow(self, path, candidate_reaction, graph) -> bool:
            raise NotImplementedError

        def should_prune(self, path, candidate_reaction, graph) -> bool:
            return False


def _path_steps(path) -> int:
    """
    path is expected to be a list: [species, reaction_id, species, ...]
    steps = number of reaction edges = (len(path) - 1)//2
    """
    try:
        return max(0, (len(path) - 1) // 2)
    except Exception:
        return 0


class CompositeRule(PathRule):
    """
    Composite rule primarily for Path-level composition (AND/OR).
    - mode: 'all' (AND) or 'any' (OR)
    Behavior:
      - is_path_allowed(path): combine child PathRule or ReactionRule results.
        * For PathRule children -> call is_path_allowed(child).
        * For ReactionRule children -> try to evaluate child on the *last reaction* on path (if any).
          If no reaction is available, treat ReactionRule child as permissive (True).
      - is_applicable(reaction): combine only ReactionRule children (if any). For PathRule children,
        we cannot decide by reaction alone, so they are treated as permissive in this method.
    This design makes CompositeRule usable both as PathRule (preferred) and to satisfy
    any existing abstract ReactionRule checks (by providing is_applicable).
    """

    def __init__(self, rules: List[Any], mode: str = "all"):
        if mode not in ("all", "any"):
            raise ValueError("mode must be 'all' or 'any'")
        self.rules = list(rules)
        self.mode = mode

    # ---------- Path-level API ----------
    def is_path_allowed(self, path) -> bool:
        """Return True if path is allowed by composite of child rules."""
        results = []
        for r in self.rules:
            # If child is PathRule-like
            if hasattr(r, "is_path_allowed") and callable(getattr(r, "is_path_allowed")):
                try:
                    results.append(bool(r.is_path_allowed(path)))
                    continue
                except Exception:
                    # on any child failure, be conservative: disallow
                    results.append(False)
                    continue

            # If child is ReactionRule-like
            if hasattr(r, "is_applicable") and callable(getattr(r, "is_applicable")):
                # try to extract last reaction from path: pattern [spec, rxn, spec, rxn, spec]
                last_reaction = None
                try:
                    if isinstance(path, (list, tuple)) and len(path) >= 2:
                        # last reaction should be at -2 position
                        candidate = path[-2]
                        last_reaction = candidate
                except Exception:
                    last_reaction = None

                if last_reaction is not None:
                    try:
                        results.append(bool(r.is_applicable(last_reaction)))
                    except Exception:
                        results.append(False)
                else:
                    # No reaction available to evaluate -> treat as permissive (True)
                    results.append(True)
                continue

            # Unknown child type -> treat permissively
            results.append(True)

        # combine according to mode
        if self.mode == "all":
            return all(results)
        else:
            return any(results)

    # ---------- Reaction-level API (for abstract compatibility) ----------
    def is_applicable(self, reaction) -> bool:
        """
        Combine ReactionRule children; for PathRule children, we don't have reaction-level
        evaluation, so treat them as permissive here.
        """
        results = []
        for r in self.rules:
            if hasattr(r, "is_applicable") and callable(getattr(r, "is_applicable")):
                try:
                    results.append(bool(r.is_applicable(reaction)))
                except Exception:
                    results.append(False)
            else:
                # PathRule children cannot be evaluated here -> treat permissive
                results.append(True)

        if self.mode == "all":
            return all(results)
        else:
            return any(results)


class DepthLimitRule(PathRule):
    def __init__(self, max_steps: int):
        self.max_steps = max_steps

    def is_path_allowed(self, path) -> bool:
        # number of reactions = (len(path) - 1) // 2
        steps = (len(path) - 1) // 2
        return steps <= self.max_steps


