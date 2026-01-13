from pathlib import Path
from src.io.reaction_index import ReactionIndex

def main():
    idx = ReactionIndex()
    base = Path(__file__).resolve().parents[2]
    idx.ingest_jsonl(base / "data" / "reactions.jsonl")

    summary = idx.summary()
    print("Reaction index summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nTop canonical collisions:")
    for k, c in sorted(idx.counts().items(), key=lambda x: -x[1])[:5]:
        print(f"{k[:16]}... : {c}")

if __name__ == "__main__":
    main()
