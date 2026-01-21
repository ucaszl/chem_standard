# tests/test_reaction.py
import json
import tempfile
import os

from chem_standard.atom import Atom
from chem_standard.molecule import Molecule
from chem_standard.reaction import Reaction


def build_H2():
    h1 = Atom(atomic_number=1, symbol="H", position=(0.0, 0.0, 0.0))
    h2 = Atom(atomic_number=1, symbol="H", position=(0.74, 0.0, 0.0))
    return Molecule(atoms=[h1, h2], metadata={"name": "H2"})


def build_O2():
    o1 = Atom(atomic_number=8, symbol="O", position=(0.0, 0.0, 0.0))
    o2 = Atom(atomic_number=8, symbol="O", position=(1.21, 0.0, 0.0))
    return Molecule(atoms=[o1, o2], metadata={"name": "O2"})


def test_reaction_as_dict_and_log(tmp_path):
    H2 = build_H2()
    O2 = build_O2()
    H2O = Molecule(
        atoms=[
            Atom(atomic_number=8, symbol="O", position=(0.0, 0.0, 0.0)),
            Atom(atomic_number=1, symbol="H", position=(0.96, 0.0, 0.0)),
            Atom(atomic_number=1, symbol="H", position=(-0.24, 0.93, 0.0)),
        ],
        metadata={"name": "H2O"},
    )

    rxn = Reaction(reactants=[H2, O2], products=[H2O], conditions={"T": 300}, metadata={"src": "test"})
    d = rxn.as_dict()
    assert "reactants" in d and isinstance(d["reactants"], list)
    assert "products" in d and isinstance(d["products"], list)
    # 妫€鏌?formula 瀛楁瀛樺湪浜?molecule dict
    assert "formula" in d["reactants"][0]

    # test log to a temp file
    out = tmp_path / "reactions.jsonl"
    path = rxn.log(sink=str(out))
    assert os.path.exists(path)
    # ensure the file contains valid json line
    with open(path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
        rec = json.loads(line)
        assert rec["metadata"]["src"] == "test"

