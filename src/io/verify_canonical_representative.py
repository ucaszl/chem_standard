from pathlib import Path
from chem_standard.dataset.reaction_dataset import ReactionDataset

def main():
    base = Path(__file__).resolve().parents[2]
    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    reps = ds.canonical_reactions()
    print("Canonical representatives:", len(reps))

    for k, r in reps.items():
        print(k[:16], "鈫?representative selected")

if __name__ == "__main__":
    main()

