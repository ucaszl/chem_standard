from pathlib import Path
from src.dataset.reaction_dataset import ReactionDataset
from src.rules.basic_rules import NonEmptyReactionRule


def main():
    base = Path(__file__).resolve().parents[2]
    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    rule = NonEmptyReactionRule()

    for r in ds.reactions():
        ok = rule.is_applicable(r)
        print(r.canonical_key()[:8], "allowed:", ok)


if __name__ == "__main__":
    main()
