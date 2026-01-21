# tests/test_api_adapter.py
import json
from chem_standard.io.api_schema import AtomInput, MoleculeInput, ReactionInput
from chem_standard.io.api_adapter import reactioninput_to_reaction, reaction_to_canonical_hash, is_duplicate, register_hash, INDEX_FILE, REACTION_LOG, DATA_DIR
from chem_standard.reaction import Reaction

def test_reaction_adapter_and_hash(tmp_path, monkeypatch):
    # prepare a small ReactionInput
    ri = ReactionInput(
        reactants=[MoleculeInput(atoms=[AtomInput(element="H", x=0, y=0, z=0), AtomInput(element="H", x=0.74, y=0, z=0)])],
        products=[MoleculeInput(atoms=[AtomInput(element="H", x=0, y=0, z=0), AtomInput(element="H", x=0.74, y=0, z=0)])],
        conditions={"temperature_K":298},
        metadata={"source":"test"}
    )
    r = reactioninput_to_reaction(ri)
    assert isinstance(r, Reaction)
    h = reaction_to_canonical_hash(r)
    # ensure hash is hex string
    assert isinstance(h, str) and len(h) == 64

def test_duplicate_index(tmp_path, monkeypatch):
    # create a fake index file
    idx = tmp_path / "index.txt"
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    # manually test register_hash / is_duplicate
    from chem_standard.io.api_adapter import _existing_hashes, register_hash, is_duplicate
    # pick a dummy hash
    h = "a" * 64
    if h in _existing_hashes:
        _existing_hashes.remove(h)
    assert not is_duplicate(h)
    register_hash(h)
    assert is_duplicate(h)

