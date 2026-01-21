# src/io/rdkit_adapter.py
from rdkit import Chem
from rdkit.Chem import AllChem
from ..atom import Atom
from ..molecule import Molecule


def molecule_from_rdkit(mol: Chem.Mol, embed_if_needed: bool = True) -> Molecule:
    """
    从 RDKit Mol 对象转换为我们的 Molecule。
    如果分子没有 3D 坐标，会尝试做一次 Embed。
    """
    if mol.GetNumConformers() == 0 and embed_if_needed:
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.UFFOptimizeMolecule(mol)

    conf = mol.GetConformer()
    atoms = []
    for rd_atom in mol.GetAtoms():
        idx = rd_atom.GetIdx()
        pos = conf.GetAtomPosition(idx)
        atom = Atom(
            atomic_number=int(rd_atom.GetAtomicNum()),
            symbol=rd_atom.GetSymbol(),
            position=(pos.x, pos.y, pos.z),
            mass=None,
            covalent_radius=None,
            properties={},
        )
        atoms.append(atom)
    return Molecule(atoms=atoms, metadata={"rdkit": True})
