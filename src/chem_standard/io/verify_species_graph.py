# src/io/verify_species_graph.py
from pathlib import Path
from chem_standard.dataset.reaction_dataset import ReactionDataset
from chem_standard.graph.species_graph import SpeciesGraph


def edge_info(edge):
    """
    鍏煎 helper锛氭帴鍙?dict (legacy) 鎴?SpeciesEdge 瀵硅薄銆?
    杩斿洖 (to, reaction_id) 鍏冪粍锛岀敤浜庢墦鍗板拰缁熻銆?
    """
    if isinstance(edge, dict):
        to = edge.get("to") or edge.get("product")
        rid = edge.get("reaction") or edge.get("reaction_id")
    else:
        # SpeciesEdge 瀵硅薄锛氫娇鐢ㄥ睘鎬ц闂?
        to = getattr(edge, "product", None)
        rid = getattr(edge, "reaction_id", getattr(edge, "reaction", None))
    return to, rid


def main():
    base = Path(__file__).resolve().parents[2]
    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    sg = SpeciesGraph.from_reaction_graph(
        # 浣跨敤 ReactionDataset 鏋勫缓 ReactionGraph 鍐嶆姇褰辨槸鏇寸ǔ濡ョ殑娴佺▼锛?
        # 浣嗘垜浠鐢ㄤ箣鍓嶇殑绠€鍗曡矾寰勶細鎸?dataset 鐨?canonical reactions 鏋勫缓 species graph
        # 浠ヤ繚璇侀獙璇佽剼鏈兘鍦ㄤ綘鐨勫綋鍓嶄粨搴撶姸鎬佷笅杩愯銆?
        __import__("src.graph.reaction_graph", fromlist=["ReactionGraph"]).ReactionGraph.from_dataset(
            ds
        )
    )

    print("Species count:", len(sg.species()))
    for s in sorted(sg.species()):
        print(s + ":")
        for e in sg.out_edges(s):
            to, rid = edge_info(e)
            # 闃插尽鎬у鐞嗭細rid 鍙兘涓?None
            rid_str = (rid[:8] + "...") if isinstance(rid, str) else str(rid)
            print("  ->", to, "(via", rid_str, ")")

if __name__ == "__main__":
    main()

