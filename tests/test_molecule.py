# tests/test_molecule.py
from ase import Atoms as ASEAtoms
from chem_standard.io.ase_adapter import molecule_from_ase, molecule_to_ase
from chem_standard.molecule import Molecule
from chem_standard.atom import Atom


def test_ase_roundtrip():
    # 绠€鍗?H2O 绀轰緥 (O + 2H)
    symbols = ["O", "H", "H"]
    positions = [(0.0, 0.0, 0.0), (0.96, 0.0, 0.0), (-0.24, 0.93, 0.0)]
    ase = ASEAtoms(symbols=symbols, positions=positions)
    mol = molecule_from_ase(ase)
    assert isinstance(mol, Molecule)
    assert len(mol) == 3
    ase2 = molecule_to_ase(mol)
    assert len(ase2) == 3
    # 妫€鏌ョ涓€涓師瀛愮鍙?
    assert ase2.get_chemical_symbols()[0] == "O"

