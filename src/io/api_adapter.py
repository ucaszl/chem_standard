from typing import Dict
from src.atom import Atom
from src.molecule import Molecule
from src.reaction import Reaction
from src.io.api_schema import AtomInput, MoleculeInput, ReactionInput

# 最小周期表（后续可系统化）
PERIODIC_TABLE: Dict[str, int] = {
    "H": 1,
    "C": 6,
    "N": 7,
    "O": 8,
}


def atom_from_input(ai: AtomInput) -> Atom:
    return Atom(
        atomic_number=PERIODIC_TABLE[ai.element],
        symbol=ai.element,
        position=[ai.x, ai.y, ai.z],
    )


def molecule_from_input(mi: MoleculeInput) -> Molecule:
    atoms = [atom_from_input(a) for a in mi.atoms]
    return Molecule(atoms=atoms, metadata=mi.metadata or {})


def reaction_from_input(ri: ReactionInput) -> Reaction:
    reactants = [molecule_from_input(m) for m in ri.reactants]
    products = [molecule_from_input(m) for m in ri.products]
    return Reaction(
        reactants=reactants,
        products=products,
        metadata=ri.metadata or {},
    )
