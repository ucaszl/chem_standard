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
