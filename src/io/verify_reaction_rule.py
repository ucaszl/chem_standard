from pathlib import Path
from chem_standard.dataset.reaction_dataset import ReactionDataset
from chem_standard.rules.basic_rules import NonEmptyReactionRule


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

