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
from chem_standard.signature.reaction_signature import ReactionSignature

class Reaction:
    """
    璇箟绾у埆鐨?Reaction 鎶借薄锛堥潪鐗╃悊姹傝В鍣級銆?
    鍙礋璐ｈ〃绀哄弽搴旓紙鍙嶅簲鐗?/ 浜х墿 / 鏉′欢 / 鍏冩暟鎹級鍙婃彁渚涙暟鎹惤鐩橀挬瀛愩€?
    """

    def __init__(
        self,
        reactants: List[Molecule],
        products: List[Molecule],
        conditions: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        # 鍙仛鏈€灏忔牎楠岋細reactants / products 蹇呴』涓?Molecule 鍒楄〃
        if not isinstance(reactants, list) or not all(isinstance(m, Molecule) for m in reactants):
            raise ValueError("reactants must be a list of Molecule instances")
        if not isinstance(products, list) or not all(isinstance(m, Molecule) for m in products):
            raise ValueError("products must be a list of Molecule instances")

        self.reactants = reactants
        self.products = products
        self.conditions = conditions or {}
        self.metadata = metadata or {}
        # 鑷姩璁板綍鍒涘缓鏃堕棿锛圲TC ISO 鏍煎紡锛?
        self.created_at = datetime.utcnow().isoformat() + "Z"

    def signature(self) -> ReactionSignature:
        """
        Return the canonical ReactionSignature for this reaction.

        Current definition (P3-2 minimal):
        - Each molecule is represented by its empirical formula string
        - Reactants and products are order-invariant
        """
        reactant_forms = tuple(
            m.formula for m in self.reactants
        )
        product_forms = tuple(
            m.formula for m in self.products
        )

        return ReactionSignature(
            reactants=reactant_forms,
            products=product_forms,
        )

    def canonical_key(self) -> str:
        """
        Backward-compatible canonical key accessor.
        """
        return self.identity().canonical_key

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
        from chem_standard.atom import Atom
        from chem_standard.molecule import Molecule

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
        杩斿洖鍙簭鍒楀寲鐨勫瓧鍏歌〃绀猴紝閫傚悎鍐欏叆鏃ュ織 / 鏁版嵁搴?/ API銆?
        浣跨敤 Molecule.to_dict() 浠ヤ繚鐣欏師瀛愮骇淇℃伅涓庡厓鏁版嵁銆?
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
        灏嗚 Reaction 鐨?as_dict() 浠ヤ竴琛?JSON锛圝SONL锛夎拷鍔犲啓鍏?sink锛堟枃浠惰矾寰勶級銆?
        榛樿 sink锛?./data/reactions.jsonl 锛堥」鐩浉瀵硅矾寰勶級
        杩斿洖鍐欏叆鐨勬枃浠惰矾寰勩€?

        娉ㄦ剰锛歞ata/ 鐩綍榛樿鍦?.gitignore 涓蹇界暐锛岀敤浜庡瓨鏀惧師濮嬫暟鎹€?
        """
        if sink is None:
            sink = os.path.join(os.getcwd(), "data", "reactions.jsonl")

        # 纭繚鐩綍瀛樺湪
        dirpath = os.path.dirname(sink)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

        record = self.as_dict()
        # 浠?UTF-8 鍐欏叆骞朵繚鎸侀潪 ASCII 鍙
        with open(sink, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return sink

    def summary(self) -> Dict[str, Any]:
        """
        杩斿洖绠€瑕佸厓淇℃伅锛堟暟閲忕骇鍒殑 summary锛夛紝渚夸簬蹇€熸煡鐪嬫垨绱㈠紩銆?
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

    def identity(self):
        """
        Return the ReactionIdentity for this reaction.
        """
        return self.signature().identity()

    def __eq__(self, other):
        if not isinstance(other, Reaction):
            return NotImplemented
        return self.identity() == other.identity()

    def __hash__(self):
        return hash(self.identity())

