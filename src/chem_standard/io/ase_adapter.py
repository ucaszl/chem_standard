# src/io/ase_adapter.py
from ase import Atoms as ASEAtoms
from ..atom import Atom
from ..molecule import Molecule
import numpy as np


def molecule_from_ase(ase_atoms: ASEAtoms) -> Molecule:
    """
    从 ASE Atoms 对象转换为自定义 Molecule。
    """
    symbols = ase_atoms.get_chemical_symbols()
    positions = ase_atoms.get_positions()
    numbers = ase_atoms.get_atomic_numbers()
    masses = ase_atoms.get_masses()
    atoms = []
    for idx, (sym, pos, num, mass) in enumerate(zip(symbols, positions, numbers, masses)):
        atom = Atom(
            atomic_number=int(num),
            symbol=str(sym),
            position=tuple(pos.tolist()),
            mass=float(mass) if mass is not None else None,
            covalent_radius=None,
            properties={},
        )
        atoms.append(atom)
    meta = {"cell": None}
    try:
        cell = ase_atoms.get_cell()
        if cell is not None:
            meta["cell"] = np.array(cell).tolist()
    except Exception:
        pass
    return Molecule(atoms=atoms, metadata=meta)


def molecule_to_ase(mol: Molecule) -> ASEAtoms:
    """
    从自定义 Molecule 转为 ASE Atoms 对象（不包含电荷/磁矩等复杂量）。
    """
    symbols = [a.symbol for a in mol.atoms]
    positions = [a.position for a in mol.atoms]
    masses = [a.mass for a in mol.atoms]
    ase = ASEAtoms(symbols=symbols, positions=positions)
    # ASE 的 set_masses 需要显式设置
    try:
        ase.set_masses([float(m) if m is not None else 0.0 for m in masses])
    except Exception:
        pass
    return ase
