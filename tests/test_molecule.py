# tests/test_molecule.py
from ase import Atoms as ASEAtoms
from src.io.ase_adapter import molecule_from_ase, molecule_to_ase
from src.molecule import Molecule
from src.atom import Atom


def test_ase_roundtrip():
    # 简单 H2O 示例 (O + 2H)
    symbols = ["O", "H", "H"]
    positions = [(0.0, 0.0, 0.0), (0.96, 0.0, 0.0), (-0.24, 0.93, 0.0)]
    ase = ASEAtoms(symbols=symbols, positions=positions)
    mol = molecule_from_ase(ase)
    assert isinstance(mol, Molecule)
    assert len(mol) == 3
    ase2 = molecule_to_ase(mol)
    assert len(ase2) == 3
    # 检查第一个原子符号
    assert ase2.get_chemical_symbols()[0] == "O"
