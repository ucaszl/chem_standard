# src/reaction.py
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
from collections import Counter
from .molecule import Molecule
from collections import defaultdict
from typing import List, Dict

class Reaction:
    """
    语义级别的 Reaction 抽象（非物理求解器）。
    只负责表示反应（反应物 / 产物 / 条件 / 元数据）及提供数据落盘钩子。
    """

    def __init__(
        self,
        reactants: List[Molecule],
        products: List[Molecule],
        conditions: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        # 只做最小校验：reactants / products 必须为 Molecule 列表
        if not isinstance(reactants, list) or not all(isinstance(m, Molecule) for m in reactants):
            raise ValueError("reactants must be a list of Molecule instances")
        if not isinstance(products, list) or not all(isinstance(m, Molecule) for m in products):
            raise ValueError("products must be a list of Molecule instances")

        self.reactants = reactants
        self.products = products
        self.conditions = conditions or {}
        self.metadata = metadata or {}
        # 自动记录创建时间（UTC ISO 格式）
        self.created_at = datetime.utcnow().isoformat() + "Z"



    def canonical_key(self) -> str:
        """
        Return a canonical, order-invariant key for reaction equivalence.

        Definition principles:
        1. Ignore ordering of reactants/products
        2. Count stoichiometry
        3. Use chemical identity only (no metadata, no kinetics)
        4. Direction-sensitive (A->B != B->A)
        """

        def normalize_side(species):
            """
            Convert a list of Molecule into a sorted, counted tuple:
            e.g. [H2, O2, O2] -> (("H2", 1), ("O2", 2))
            """
            names = [m.formula for m in species]
            counter = Counter(names)
            return tuple(sorted(counter.items()))

        reactant_sig = normalize_side(self.reactants)
        product_sig = normalize_side(self.products)

        canonical_repr = {
            "reactants": reactant_sig,
            "products": product_sig,
        }

        raw = repr(canonical_repr).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def deduplicate(reactions: List["Reaction"]) -> Dict[str, List["Reaction"]]:
        """
        Group reactions by canonical_key.

        Returns
        -------
        dict
            canonical_key -> list of equivalent Reaction objects
        """
        buckets: Dict[str, List[Reaction]] = defaultdict(list)

        for r in reactions:
            key = r.canonical_key()
            buckets[key].append(r)

        return dict(buckets)

    @classmethod
    def from_dict(cls, d: dict) -> "Reaction":
        from src.atom import Atom
        from src.molecule import Molecule

        def atom_from_dict(ad):
            return Atom(
                atomic_number=ad["atomic_number"],
                symbol=ad["symbol"],
                position=tuple(ad["position"]),
                mass=ad.get("mass"),
                covalent_radius=ad.get("covalent_radius"),
                properties=ad.get("properties", {}),
            )

        def molecule_from_dict(md):
            atoms = [atom_from_dict(a) for a in md["atoms"]]
            return Molecule(atoms=atoms, metadata=md.get("metadata", {}))

        reactants = [molecule_from_dict(m) for m in d["reactants"]]
        products = [molecule_from_dict(m) for m in d["products"]]

        return cls(
            reactants=reactants,
            products=products,
            conditions=d.get("conditions", {}),
            metadata=d.get("metadata", {}),
        )

    def as_dict(self) -> Dict[str, Any]:
        """
        返回可序列化的字典表示，适合写入日志 / 数据库 / API。
        使用 Molecule.to_dict() 以保留原子级信息与元数据。
        """
        return {
            "reactants": [m.to_dict() for m in self.reactants],
            "products": [m.to_dict() for m in self.products],
            "conditions": self.conditions,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    def log(self, sink: Optional[str] = None) -> str:
        """
        将该 Reaction 的 as_dict() 以一行 JSON（JSONL）追加写入 sink（文件路径）。
        默认 sink： ./data/reactions.jsonl （项目相对路径）
        返回写入的文件路径。

        注意：data/ 目录默认在 .gitignore 中被忽略，用于存放原始数据。
        """
        if sink is None:
            sink = os.path.join(os.getcwd(), "data", "reactions.jsonl")

        # 确保目录存在
        dirpath = os.path.dirname(sink)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        record = self.as_dict()
        # 以 UTF-8 写入并保持非 ASCII 可读
        with open(sink, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return sink

    def summary(self) -> Dict[str, Any]:
        """
        返回简要元信息（数量级别的 summary），便于快速查看或索引。
        """
        return {
            "n_reactants": len(self.reactants),
            "n_products": len(self.products),
            "conditions": self.conditions,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    def __repr__(self):
        return f"Reaction(reactants={len(self.reactants)}, products={len(self.products)}, created_at={self.created_at})"
