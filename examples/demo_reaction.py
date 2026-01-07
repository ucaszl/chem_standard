# examples/demo_reaction.py
from src.atom import Atom
from src.molecule import Molecule
from src.reaction import Reaction

def build_H2():
    # 两个氢原子（示例位置，单位 Å）
    h1 = Atom(atomic_number=1, symbol="H", position=(0.0, 0.0, 0.0))
    h2 = Atom(atomic_number=1, symbol="H", position=(0.74, 0.0, 0.0))
    return Molecule(atoms=[h1, h2], metadata={"name": "H2"})

def build_O2():
    o1 = Atom(atomic_number=8, symbol="O", position=(0.0, 0.0, 0.0))
    o2 = Atom(atomic_number=8, symbol="O", position=(1.21, 0.0, 0.0))
    return Molecule(atoms=[o1, o2], metadata={"name": "O2"})

def build_H2O():
    o = Atom(atomic_number=8, symbol="O", position=(0.0, 0.0, 0.0))
    h1 = Atom(atomic_number=1, symbol="H", position=(0.96, 0.0, 0.0))
    h2 = Atom(atomic_number=1, symbol="H", position=(-0.24, 0.93, 0.0))
    return Molecule(atoms=[o, h1, h2], metadata={"name": "H2O"})

def main():
    H2 = build_H2()
    O2 = build_O2()
    H2O = build_H2O()

    rxn = Reaction(
        reactants=[H2, O2],
        products=[H2O],
        conditions={"temperature_K": 298, "pressure_atm": 1.0},
        metadata={"source": "demo_reaction", "notes": "stoichiometry simplified"}
    )

    # 打印结构化字典（可直接被 ML 管线消费）
    print("Reaction as dict:")
    d = rxn.as_dict()
    # 为了可读性简短打印：显示 summary + reactants/products counts
    print(rxn.summary())
    # 写入本地 data/reactions.jsonl，并打印路径
    out = rxn.log()
    print(f"Logged reaction to: {out}")
    # 打印第一个 reactant 的原子基本信息作为快速验证
    print("Reactant 0 first atom:", d["reactants"][0]["atoms"][0])

if __name__ == "__main__":
    main()
