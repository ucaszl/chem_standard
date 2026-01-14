from pathlib import Path
from src.dataset.reaction_dataset import ReactionDataset


def main():
    base = Path(__file__).resolve().parents[2]
    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    stats = ds.stats()
    print("ReactionDataset stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    reps = ds.canonical_reactions()
    print("Canonical representatives:", len(reps))


if __name__ == "__main__":
    main()
