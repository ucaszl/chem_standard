from pathlib import Path
from src.dataset.reaction_dataset import ReactionDataset
from src.graph.species_graph import SpeciesGraph

def main():
    base = Path(__file__).resolve().parents[2]
    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    sg = SpeciesGraph()
    for r in ds.canonical_reactions().values():
        sg.add_reaction(r)

    print("Species count:", len(sg.species()))
    for s in sorted(sg.species()):
        print(f"{s}:")
        for e in sg.successors(s):
            print("  ->", e["to"], "(via", e["reaction"][:8], ")")

if __name__ == "__main__":
    main()
