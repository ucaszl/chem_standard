from pathlib import Path
from chem_standard.dataset.reaction_dataset import ReactionDataset
from chem_standard.graph.reaction_graph import ReactionGraph
from chem_standard.graph.species_graph import SpeciesGraph
from chem_standard.path.reaction_path_finder import ReactionPathFinder


def main():
    base = Path(__file__).resolve().parents[2]

    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    rg = ReactionGraph()
    for r in ds.reactions():
        rg.add_reaction(r)

    sg = SpeciesGraph.from_reaction_graph(rg)

    finder = ReactionPathFinder(sg)

    paths = finder.find_paths("H2", "H2", max_depth=3)

    print("Found paths:")
    for p in paths:
        print("  ", " -> ".join(p))


if __name__ == "__main__":
    main()

