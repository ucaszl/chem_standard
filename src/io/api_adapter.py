# src/io/api_adapter.py
from typing import Dict, List
from pathlib import Path
import json
import hashlib
from datetime import datetime
from chem_standard.atom import Atom
from chem_standard.molecule import Molecule
from chem_standard.reaction import Reaction
from chem_standard.io.api_schema import AtomInput, MoleculeInput, ReactionInput

# 鏈€灏忓厓绱犺〃锛堟牴鎹渶瑕佹墿灞曪級
PERIODIC_TABLE: Dict[str, int] = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
    # 鍙垪涓惧父鐢ㄩ」锛屽悗缁鎵╁厖瀹屾暣琛?
}

# 鏁版嵁鐩綍涓庣储寮曟枃浠讹紙涓?API 淇濇寔涓€鑷达級
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # points to project root
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
REACTION_LOG = DATA_DIR / "reactions.jsonl"
INDEX_FILE = DATA_DIR / "reactions_index.txt"

# 鍔犺浇宸叉湁 hash 绱㈠紩鍒板唴瀛橈紙绠€鍗曟寔涔呭寲锛?
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
    浜х敓涓€涓?canonical json 鍝堝笇锛岀敤浜庡幓閲嶃€?
    鎴戜滑瀵?reactants/products 鍋氭帓搴忥紙鎸夊厓绱犵鍙峰強鍧愭爣锛夛紝浠ュ噺灏忛『搴忓鑷寸殑宸紓銆?
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
    # 鍐欏叆 jsonl锛坮 涓?core.Reaction锛?
    with REACTION_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

