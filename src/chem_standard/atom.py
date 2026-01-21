# src/atom.py
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Tuple
import numpy as np


@dataclass
class Atom:
    """
    最小的 Atom 数据结构。
    - atomic_number: 元素序数（int）
    - symbol: 化学符号（str，例如 "C"）
    - position: 3 元素数组或可转为 numpy.array 的序列（单位：Å）
    - mass: 可选（float）
    - covalent_radius: 可选（float）
    - properties: 额外属性字典
    """
    atomic_number: int
    symbol: str
    position: Tuple[float, float, float]
    mass: Optional[float] = None
    covalent_radius: Optional[float] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        pos = np.asarray(self.position, dtype=float)
        if pos.shape != (3,):
            raise ValueError("position must be a length-3 sequence")
        # 规范化存储为 numpy 数组
        self.position = pos

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # numpy array 转为列表便于序列化
        d["position"] = [float(x) for x in self.position]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Atom":
        return cls(
            atomic_number=int(data["atomic_number"]),
            symbol=str(data["symbol"]),
            position=tuple(data["position"]),
            mass=data.get("mass"),
            covalent_radius=data.get("covalent_radius"),
            properties=data.get("properties", {}),
        )
