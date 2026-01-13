from collections import defaultdict
from pathlib import Path
import json
from typing import Dict
from src.reaction import Reaction

class ReactionDataset:
    def __init__(self):
        self._by_key = defaultdict(list)

    def load_jsonl(self, path: Path):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = Reaction.from_dict(json.loads(line))
                self._by_key[r.canonical_key()].append(r)

    @property
    def total(self) -> int:
        return sum(len(v) for v in self._by_key.values())

    @property
    def unique(self) -> int:
        return len(self._by_key)

    def collisions(self):
        return {k: len(v) for k, v in self._by_key.items() if len(v) > 1}

    def canonical_reactions(self) -> Dict[str, Reaction]:
        """
        For each canonical_key, choose one representative Reaction.

        Strategy:
        - Serialize each reaction to dict
        - Sort by the JSON string (stable, deterministic)
        - Pick the first one
        """
        reps = {}
        for key, reactions in self._by_key.items():
            reps[key] = sorted(
                reactions,
                key=lambda r: json.dumps(
                    r.as_dict(),
                    sort_keys=True,
                    ensure_ascii=False
                )
            )[0]
        return reps