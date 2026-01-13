# src/io/api_adapter.py
from typing import Dict, List
from pathlib import Path
import json
import hashlib
from datetime import datetime
from src.atom import Atom
from src.molecule import Molecule
from src.reaction import Reaction
from src.io.api_schema import AtomInput, MoleculeInput, ReactionInput

# 最小元素表（根据需要扩展）
PERIODIC_TABLE: Dict[str, int] = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
    # 只列举常用项，后续请扩充完整表
}

# 数据目录与索引文件（与 API 保持一致）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # points to project root
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
REACTION_LOG = DATA_DIR / "reactions.jsonl"
INDEX_FILE = DATA_DIR / "reactions_index.txt"

# 加载已有 hash 索引到内存（简单持久化）
_existing_hashes = set()
if INDEX_FILE.exists():
    try:
        with INDEX_FILE.open("r", encoding="utf-8") as f:
            for ln in f:
                h = ln.strip()
                if h:
                    _existing_hashes.add(h)
    except Exception:
        _existing_hashes = set()


def _atominput_to_atom(ai: AtomInput) -> Atom:
    # try element symbol or name -> atomic_number
    symbol = ai.element
    if isinstance(symbol, str):
        sym = symbol.strip()
    else:
        raise ValueError("element must be a string symbol, e.g. 'H'")

    if sym in PERIODIC_TABLE:
        z = PERIODIC_TABLE[sym]
    else:
        # fallback: if user provided a number string like "6" or "C"
        try:
            z = int(sym)
        except Exception:
            raise ValueError(f"Unknown element symbol: {sym}")

    pos = tuple(float(x) for x in (ai.x, ai.y, ai.z))
    if len(pos) != 3:
        raise ValueError("position must be three floats")
    return Atom(atomic_number=z, symbol=sym, position=pos)


def moleculeinput_to_molecule(mi: MoleculeInput) -> Molecule:
    atoms: List[Atom] = [_atominput_to_atom(a) for a in mi.atoms]
    return Molecule(atoms=atoms, metadata=mi.metadata or {})


def reactioninput_to_reaction(ri: ReactionInput) -> Reaction:
    reactants = [moleculeinput_to_molecule(m) for m in ri.reactants]
    products = [moleculeinput_to_molecule(m) for m in ri.products]
    # reaction object will populate reaction_id, created_at, schema_version by default
    return Reaction(reactants=reactants, products=products, conditions=ri.conditions or {}, metadata=ri.metadata or {})


def reaction_to_canonical_hash(r: Reaction) -> str:
    """
    产生一个 canonical json 哈希，用于去重。
    我们对 reactants/products 做排序（按元素符号及坐标），以减小顺序导致的差异。
    """
    def canonical_mol(mol):
        atoms = sorted([
            {"symbol": a.symbol, "pos": [round(float(x), 8) for x in a.position]}
            for a in mol.atoms
        ], key=lambda x: (x["symbol"], x["pos"]))
        return {"atoms": atoms, "metadata": mol.metadata}

    canonical = {
        "reactants": [canonical_mol(m) for m in r.reactants],
        "products": [canonical_mol(m) for m in r.products],
        "conditions": r.conditions,
    }
    j = json.dumps(canonical, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    h = hashlib.sha256(j.encode("utf-8")).hexdigest()
    return h


def is_duplicate(hash_str: str) -> bool:
    return hash_str in _existing_hashes


def register_hash(hash_str: str):
    # append to disk and memory set
    _existing_hashes.add(hash_str)
    with INDEX_FILE.open("a", encoding="utf-8") as f:
        f.write(hash_str + "\n")


def write_reaction(r: Reaction):
    # 写入 jsonl（r 为 core.Reaction）
    with REACTION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
