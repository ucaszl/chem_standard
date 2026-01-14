from pathlib import Path
import json
from collections import defaultdict
from src.reaction import Reaction


class ReactionDataset:
    def __init__(self):
        self._reactions = []
        self._by_canonical = defaultdict(list)

    def load_jsonl(self, path: Path):
        """
        Load reactions from a jsonl file.
        Each line must be a Reaction-compatible dict.
        """
        self._reactions.clear()
        self._by_canonical.clear()

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                r = Reaction.from_dict(d)
                self._reactions.append(r)
                self._by_canonical[r.canonical_key()].append(r)

    def reactions(self):
        """Return all reactions (raw list)."""
        return list(self._reactions)

    def canonical_reactions(self):
        """
        Return one representative Reaction per canonical_key.
        Selection rule: first occurrence.
        """
        return {
            k: v[0]
            for k, v in self._by_canonical.items()
        }

    def stats(self):
        """Return dataset-level statistics."""
        return {
            "total_reactions": len(self._reactions),
            "unique_reactions": len(self._by_canonical),
        }
