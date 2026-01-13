import json
from pathlib import Path
from collections import defaultdict

from src.atom import Atom
from src.molecule import Molecule
from src.reaction import Reaction


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "reactions.jsonl"


def load_reactions(path: Path):
    reactions = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)

            reactants = [
                Molecule(
                    atoms=[Atom(**a) for a in m["atoms"]],
                    metadata=m.get("metadata"),
                )
                for m in obj["reactants"]
            ]

            products = [
                Molecule(
                    atoms=[Atom(**a) for a in m["atoms"]],
                    metadata=m.get("metadata"),
                )
                for m in obj["products"]
            ]

            reactions.append(
                Reaction(
                    reactants=reactants,
                    products=products,
                    metadata=obj.get("metadata"),
                )
            )

    return reactions


def main():
    reactions = load_reactions(DATA_PATH)

    buckets = Reaction.deduplicate(reactions)


    total = len(reactions)
    unique = len(buckets)

    print(f"Total reactions: {total}")
    print(f"Unique canonical reactions: {unique}")
    print(f"Deduplicated: {total - unique}")

    # Optional: show collisions (same key, multiple entries)
    print("\nCanonical collisions (key → count):")
    for k, rs in buckets.items():
        if len(rs) > 1:
            print(f"{k[:16]}... : {len(rs)}")


if __name__ == "__main__":
    main()
