# examples/demo_reaction.py
from chem_standard.atom import Atom
from chem_standard.molecule import Molecule
from chem_standard.reaction import Reaction

def build_H2():
    # 涓や釜姘㈠師瀛愶紙绀轰緥浣嶇疆锛屽崟浣?脜锛?
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

    # 鎵撳嵃缁撴瀯鍖栧瓧鍏革紙鍙洿鎺ヨ ML 绠＄嚎娑堣垂锛?
    print("Reaction as dict:")
    d = rxn.as_dict()
    # 涓轰簡鍙鎬х畝鐭墦鍗帮細鏄剧ず summary + reactants/products counts
    print(rxn.summary())
    # 鍐欏叆鏈湴 data/reactions.jsonl锛屽苟鎵撳嵃璺緞
    out = rxn.log()
    print(f"Logged reaction to: {out}")
    # 鎵撳嵃绗竴涓?reactant 鐨勫師瀛愬熀鏈俊鎭綔涓哄揩閫熼獙璇?
    print("Reactant 0 first atom:", d["reactants"][0]["atoms"][0])

if __name__ == "__main__":
    main()

