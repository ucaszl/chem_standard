# src/io/verify_species_graph.py
from pathlib import Path
from src.dataset.reaction_dataset import ReactionDataset
from src.graph.species_graph import SpeciesGraph


def edge_info(edge):
    """
    兼容 helper：接受 dict (legacy) 或 SpeciesEdge 对象。
    返回 (to, reaction_id) 元组，用于打印和统计。
    """
    if isinstance(edge, dict):
        to = edge.get("to") or edge.get("product")
        rid = edge.get("reaction") or edge.get("reaction_id")
    else:
        # SpeciesEdge 对象：使用属性访问
        to = getattr(edge, "product", None)
        rid = getattr(edge, "reaction_id", getattr(edge, "reaction", None))
    return to, rid


def main():
    base = Path(__file__).resolve().parents[2]
    ds = ReactionDataset()
    ds.load_jsonl(base / "data" / "reactions.jsonl")

    sg = SpeciesGraph.from_reaction_graph(
        # 使用 ReactionDataset 构建 ReactionGraph 再投影是更稳妥的流程，
        # 但我们复用之前的简单路径：按 dataset 的 canonical reactions 构建 species graph
        # 以保证验证脚本能在你的当前仓库状态下运行。
        __import__("src.graph.reaction_graph", fromlist=["ReactionGraph"]).ReactionGraph.from_dataset(
            ds
        )
    )

    print("Species count:", len(sg.species()))
    for s in sorted(sg.species()):
        print(s + ":")
        for e in sg.out_edges(s):
            to, rid = edge_info(e)
            # 防御性处理：rid 可能为 None
            rid_str = (rid[:8] + "...") if isinstance(rid, str) else str(rid)
            print("  ->", to, "(via", rid_str, ")")

if __name__ == "__main__":
    main()
