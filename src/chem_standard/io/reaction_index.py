from collections import defaultdict
import json
from pathlib import Path
from chem_standard.reaction import Reaction

class ReactionIndex:
    def __init__(self):
        self._index = defaultdict(list)

    def ingest_jsonl(self, path: Path):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                r = Reaction.from_dict(d)
                key = r.canonical_key()
                self._index[key].append(r)

    def summary(self):
        return {
            "total_reactions": sum(len(v) for v in self._index.values()),
            "unique_reactions": len(self._index),
        }

    def counts(self):
        return {k: len(v) for k, v in self._index.items()}

