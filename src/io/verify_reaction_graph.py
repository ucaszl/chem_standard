from pathlib import Path

from src.dataset.reaction_dataset import ReactionDataset
from src.graph.reaction_graph import ReactionGraph


def main():
    base = Path(__file__).resolve().parents[2]

    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    g = ReactionGraph()
    g.add_reactions(ds.reactions())

    print("ReactionGraph stats:")
    for k, v in g.stats().items():
        print(f"  {k}: {v}")

    print("\nQuery by species:")
    for sp in ["H2", "O2", "CO2"]:
        rs = g.reactions_by_species(sp)
        print(f"  {sp}: {len(rs)} reactions")


if __name__ == "__main__":
    main()
