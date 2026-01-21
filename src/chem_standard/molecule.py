# src/molecule.py
from typing import List, Optional, Dict, Any
from .atom import Atom
import numpy as np
from collections import Counter


class Molecule:
    """
    Molecule: 一组 Atom 对象以及元数据。
    提供常用的帮助函数（positions、center_of_mass、to_dict、from_dict）。
    新增：formula 属性（例如 "H2O"），根据 atom.symbol 自动生成。
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

    @property
    def formula(self) -> str:
        """
        Simple formula generator:
        - Count element symbols (case-sensitive by symbol).
        - Return a compact formula like C6H6O or H2O (sorted by Hill system not implemented;
          we use alphabetical ordering for reproducibility here).
        """
        symbols = [a.symbol for a in self.atoms]
        counts = Counter(symbols)
        # Sort keys for reproducible output: alphabetical
        parts = []
        for el in sorted(counts.keys()):
            n = counts[el]
            parts.append(f"{el}" + (str(n) if n > 1 else ""))
        return "".join(parts)

    def to_dict(self) -> Dict:
        """
        Include atoms, metadata, and computed formula to aid downstream ML pipelines.
        """
        return {
            "atoms": [a.to_dict() for a in self.atoms],
            "metadata": self.metadata,
            "formula": self.formula,
            "n_atoms": len(self.atoms),
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
        return f"Molecule(num_atoms={len(self.atoms)}, formula={self.formula}, metadata={self.metadata})"
