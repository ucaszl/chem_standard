from typing import List, Dict, Optional
from pydantic import BaseModel


class AtomInput(BaseModel):
    element: str
    x: float
    y: float
    z: float

class MoleculeInput(BaseModel):
    atoms: List[AtomInput]
    metadata: Optional[Dict] = None


class ReactionInput(BaseModel):
    reactants: list[MoleculeInput]
    products: list[MoleculeInput]
    conditions: dict | None = None
    metadata: dict | None = None

