# chem_standard (MVP)

这是一个最小化的原子/分子标准化骨架：
- `Atom`、`Molecule` 基类
- ASE / RDKit IO 适配器
- 示例 demo 与单元测试

快速开始：
1. 创建 conda 环境并安装依赖（见 instruction）
2. 运行 `pytest` 确认测试通过
3. 运行 `python examples/demo_load.py` 查看 demo

目标：构建统一的抽象层以便接入 QM / 力场 / ML 后端。

## Reaction Abstraction (Draft)

`Reaction` provides a semantic-level representation of chemical transformations:
- `reactants` / `products` are lists of `Molecule` objects (see `src/molecule.py`).
- `conditions` is a free-form dict (temperature, pressure, solvent, etc.).
- `metadata` stores provenance (source, notes, dataset id).

The design intent:
1. Keep the representation **non-physical** and **data-centric** (no DFT/energies).
2. Provide a consistent **data hook** (`Reaction.log`) that appends JSONL records
   to `data/reactions.jsonl` for downstream ML pipelines and curation.
3. Serve as the protocol layer enabling future backends (DFT, MD, ML) to attach
   computed properties while keeping the same semantic schema.

This file is a draft; the Reaction schema will be iterated as we gather usage and data.

