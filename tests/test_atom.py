# tests/test_atom.py
import numpy as np
from src.atom import Atom


def test_atom_basic():
    a = Atom(atomic_number=8, symbol="O", position=(0.0, 0.1, -0.2), mass=15.999)
    assert a.symbol == "O"
    assert a.atomic_number == 8
    pos = np.array([0.0, 0.1, -0.2])
    assert np.allclose(a.position, pos)
    d = a.to_dict()
    assert d["symbol"] == "O"
    a2 = Atom.from_dict(d)
    assert a2.atomic_number == a.atomic_number
    assert np.allclose(a2.position, a.position)
