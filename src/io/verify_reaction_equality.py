from pathlib import Path
from chem_standard.dataset.reaction_dataset import ReactionDataset

def main():
    base = Path(__file__).resolve().parents[2]
    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    reactions = ds.reactions()
    r1, r2 = reactions[0], reactions[1]

    print("r1 == r2:", r1 == r2)
    print("len(set(reactions)):", len(set(reactions)))

if __name__ == "__main__":
    main()

