# src/io/verify_rule_minimal.py
"""
Minimal verification: ensure CompositeRule + DepthLimitRule work with your ReactionPathFinder.
Run: python src/io/verify_rule_minimal.py
"""

import traceback

from src.rules.reaction_rule_composition import CompositeRule, DepthLimitRule

# 尝试导入仓库内的 ReactionPathFinder / SpeciesGraph
REAL = True
try:
    from src.path.reaction_path_finder import ReactionPathFinder  # type: ignore
    from src.graph.species_graph import SpeciesGraph  # type: ignore
except Exception:
    REAL = False

if not REAL:
    print("[verify_minimal] real ReactionPathFinder not available, using mock finder + graph for smoke test.")

    class MockGraph:
        def __init__(self):
            self._out = {
                "A": [{"to": "B", "reaction": "r1"}, {"to": "C", "reaction": "r2"}],
                "B": [{"to": "C", "reaction": "r3"}, {"to": "D", "reaction": "r4"}],
                "C": [{"to": "D", "reaction": "r5"}],
                "D": []
            }

        def out_edges(self, s):
            return self._out.get(s, [])

    class MockFinder:
        def __init__(self, graph, rules=None):
            self.graph = graph
            self.rules = list(rules or [])

        def find_paths(self, start, target, max_depth=5):
            results = []
            stack = [(start, [start])]
            while stack:
                node, path = stack.pop()
                if node == target and len(path) > 1:
                    results.append(path)
                    continue
                if (len(path) - 1) // 2 >= max_depth:
                    continue
                for edge in self.graph.out_edges(node):
                    next_s = edge.get("to")
                    # early prune via should_prune
                    pruned = False
                    for r in self.rules:
                        fn = getattr(r, "should_prune", None)
                        if callable(fn) and fn(path, edge.get("reaction"), self.graph):
                            pruned = True
                            break
                    if pruned:
                        continue
                    allowed = True
                    for r in self.rules:
                        fn = getattr(r, "allow", None)
                        if callable(fn) and not fn(path + [edge.get("reaction"), next_s], edge.get("reaction"), self.graph):
                            allowed = False
                            break
                    if not allowed:
                        continue
                    stack.append((next_s, path + [edge.get("reaction"), next_s]))
            return results

    FinderClass = MockFinder
    GraphClass = MockGraph
else:
    FinderClass = ReactionPathFinder
    GraphClass = SpeciesGraph

def run():
    try:
        g = GraphClass()
        depth_rule = DepthLimitRule(max_steps=2)
        composite = CompositeRule([depth_rule], mode="all")
        finder = FinderClass(g, rules=[composite]) if REAL else FinderClass(g, rules=[composite])
        paths = finder.find_paths("A", "D", max_depth=5)
        print("Found paths (bounded by depth 2):", paths)
        # if depth limit is 2 steps, any found path should have steps <=2
        for p in paths:
            steps = (len(p) - 1) // 2
            assert steps <= 2, f"exceeded depth: {p}"
        print("verify_rule_minimal: PASS")
    except AssertionError as e:
        print("Assertion failed:", e)
        traceback.print_exc()
        raise
    except Exception as e:
        print("ERROR in verify_rule_minimal:", e)
        traceback.print_exc()
        raise

if __name__ == "__main__":
    run()
