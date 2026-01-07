# src/molecule.py
from typing import List, Optional, Dict, Any
from .atom import Atom
import numpy as np


class Molecule:
    """
    Molecule: 一组 Atom 对象以及元数据。
    提供常用的帮助函数（positions、center_of_mass、to_dict、from_dict）。
    """

    def __init__(self, atoms: List[Atom], metadata: Optional[Dict[str, Any]] = None):
        if not isinstance(atoms, list):
            raise ValueError("atoms must be a list of Atom instances")
        for a in atoms:
            if not isinstance(a, Atom):
                raise ValueError("all elements of atoms must be Atom instances")
        self.atoms = atoms
        self.metadata = metadata or {}

    @property
    def positions(self) -> np.ndarray:
        return np.vstack([a.position for a in self.atoms])

    @property
    def atomic_numbers(self) -> List[int]:
        return [a.atomic_number for a in self.atoms]

    def center_of_mass(self) -> np.ndarray:
        masses = np.array([a.mass if a.mass is not None else 1.0 for a in self.atoms], dtype=float)
        pos = self.positions
        return (masses[:, None] * pos).sum(axis=0) / masses.sum()

    def to_dict(self) -> Dict:
        return {
            "atoms": [a.to_dict() for a in self.atoms],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Molecule":
        atoms = [Atom.from_dict(ad) for ad in data["atoms"]]
        return cls(atoms=atoms, metadata=data.get("metadata", {}))

    def add_atom(self, atom: Atom):
        if not isinstance(atom, Atom):
            raise ValueError("atom must be an Atom instance")
        self.atoms.append(atom)

    def __len__(self):
        return len(self.atoms)

    def __repr__(self):
        return f"Molecule(num_atoms={len(self.atoms)}, metadata={self.metadata})"
