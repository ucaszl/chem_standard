from pathlib import Path
from src.dataset.reaction_dataset import ReactionDataset

def main():
    base = Path(__file__).resolve().parents[2]
    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    print("Total:", ds.total)
    print("Unique:", ds.unique)
    print("Collisions:")
    for k, v in ds.collisions().items():
        print(k[:16], "→", v)

if __name__ == "__main__":
    main()
