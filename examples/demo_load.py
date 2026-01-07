# examples/demo_load.py
from ase import Atoms as ASEAtoms
from src.io.ase_adapter import molecule_from_ase

def main():
    symbols = ["O", "H", "H"]
    positions = [(0.0, 0.0, 0.0), (0.96, 0.0, 0.0), (-0.24, 0.93, 0.0)]
    ase = ASEAtoms(symbols=symbols, positions=positions)
    mol = molecule_from_ase(ase)
    print("Converted Molecule:", mol)
    for i, a in enumerate(mol.atoms):
        print(i, a.symbol, a.atomic_number, a.position.tolist())

if __name__ == "__main__":
    main()
