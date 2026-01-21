# src/io/verify_rule_filtered_paths.py

from pathlib import Path

from chem_standard.dataset.reaction_dataset import ReactionDataset
from chem_standard.graph.reaction_graph import ReactionGraph
from chem_standard.graph.species_graph import SpeciesGraph
from chem_standard.path.reaction_path_finder import ReactionPathFinder
from chem_standard.rules.reaction_rule import ReactionRule


class AllowAllRule(ReactionRule):
    """
    Trivial rule: allow all reactions.
    Used to verify that rule-injection does not change behavior.
    """

    def is_applicable(self, reaction) -> bool:
        return True


def main():
    base = Path(__file__).resolve().parents[2]

    # 1. Load dataset
    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    # 2. Build ReactionGraph
    rg = ReactionGraph()
    rg.add_reactions(ds.reactions())

    # 3. Build SpeciesGraph
    sg = SpeciesGraph.from_reaction_graph(rg)

    start = "H2"
    target = "H2"

    # 4. PathFinder WITHOUT rule
    finder_plain = ReactionPathFinder(sg)
    paths_plain = finder_plain.find_paths(start, target, max_depth=3)

    # 5. PathFinder WITH trivial rule
    finder_rule = ReactionPathFinder(sg, rule=AllowAllRule())
    paths_rule = finder_rule.find_paths(start, target, max_depth=3)

    print("Paths without rule:", len(paths_plain))
    print("Paths with AllowAllRule:", len(paths_rule))

    assert len(paths_plain) == len(paths_rule), \
        "Rule-injected pathfinder should match plain pathfinder for AllowAllRule"

    print("鉁?Rule filtering is structurally correct")


if __name__ == "__main__":
    main()

