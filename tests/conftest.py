# tests/conftest.py
import sys
from pathlib import Path

# 插入项目根到 sys.path（保证无论 pytest 从何处启动都能 import src）
ROOT = Path(__file__).resolve().parent.parent
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)
