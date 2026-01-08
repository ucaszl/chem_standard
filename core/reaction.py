# chem_standard/core/reaction.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


# =====================
# 基础原子 / 分子抽象
# =====================

@dataclass(frozen=True)
class Atom:
    atomic_number: int
    symbol: str
    position: tuple[float, float, float]

    mass: Optional[float] = None
    covalent_radius: Optional[float] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if len(self.position) != 3:
            raise ValueError("Atom.position must be a 3-tuple (x, y, z)")


@dataclass
class Molecule:
    atoms: List[Atom]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def formula(self) -> Dict[str, int]:
        """
        返回元素计数，例如 {"H": 2, "O": 1}
        """
        counts: Dict[str, int] = {}
        for atom in self.atoms:
            counts[atom.symbol] = counts.get(atom.symbol, 0) + 1
        return counts


# =====================
# Reaction 核心抽象
# =====================

@dataclass
class Reaction:
    reactants: List[Molecule]
    products: List[Molecule]

    # 物理 / 化学条件（唯一允许放物理量的地方）
    conditions: Dict[str, Any] = field(default_factory=dict)

    # 数据来源、标注、备注（禁止放物理量）
    metadata: Dict[str, Any] = field(default_factory=dict)

    # 系统字段
    reaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    schema_version: str = "reaction.v1"

    # =====================
    # 不可退让的校验
    # =====================

    def __post_init__(self):
        if not self.reactants:
            raise ValueError("Reaction must have at least one reactant")
        if not self.products:
            raise ValueError("Reaction must have at least one product")

        # 禁止在 metadata 中混入物理条件
        forbidden_keys = {"temperature", "pressure", "potential", "energy"}
        overlap = forbidden_keys & self.metadata.keys()
        if overlap:
            raise ValueError(
                f"Physical parameters {overlap} must be placed in `conditions`, not metadata"
            )

    # =====================
    # 核心语义方法
    # =====================

    def reactant_formulae(self) -> List[Dict[str, int]]:
        return [mol.formula() for mol in self.reactants]

    def product_formulae(self) -> List[Dict[str, int]]:
        return [mol.formula() for mol in self.products]

    def is_balanced(self) -> bool:
        """
        元素守恒检查（不考虑电荷、同位素）
        """
        def aggregate(formulae: List[Dict[str, int]]) -> Dict[str, int]:
            total: Dict[str, int] = {}
            for f in formulae:
                for k, v in f.items():
                    total[k] = total.get(k, 0) + v
            return total

        return (
            aggregate(self.reactant_formulae())
            == aggregate(self.product_formulae())
        )

    # =====================
    # 序列化（用于 API / 数据集）
    # =====================

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reaction_id": self.reaction_id,
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "reactants": [self._molecule_to_dict(m) for m in self.reactants],
            "products": [self._molecule_to_dict(m) for m in self.products],
            "conditions": self.conditions,
            "metadata": self.metadata,
        }

    @staticmethod
    def _molecule_to_dict(mol: Molecule) -> Dict[str, Any]:
        return {
            "atoms": [
                {
                    "atomic_number": a.atomic_number,
                    "symbol": a.symbol,
                    "position": list(a.position),
                    "mass": a.mass,
                    "covalent_radius": a.covalent_radius,
                    "properties": a.properties,
                }
                for a in mol.atoms
            ],
            "metadata": mol.metadata,
        }
