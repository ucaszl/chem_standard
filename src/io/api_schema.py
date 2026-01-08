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
    reactants: List[MoleculeInput]
    products: List[MoleculeInput]
    metadata: Optional[Dict] = None
