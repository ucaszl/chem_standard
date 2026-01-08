# examples/api_reaction.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import uuid
import threading

app = FastAPI(title="chem-standard Reaction API", version="0.2")

# =====================
# 全局写入锁（最小并发安全）
# =====================
_write_lock = threading.Lock()

# =====================
# 数据模型
# =====================

class AtomPayload(BaseModel):
    atomic_number: int
    symbol: str
    position: List[float] = Field(
        ...,
        description="Cartesian coordinates [x, y, z]"
    )

    mass: Optional[float] = None
    covalent_radius: Optional[float] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("position", mode="before")
    @classmethod
    def check_position_dim(cls, v):
        if not isinstance(v, (list, tuple)):
            raise ValueError("position must be a list [x, y, z]")
        if len(v) != 3:
            raise ValueError("position must be [x, y, z]")
        return v


class MoleculePayload(BaseModel):
    atoms: List[AtomPayload]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReactionPayload(BaseModel):
    reactants: List[MoleculePayload]
    products: List[MoleculePayload]

    # 物理 / 化学条件（必须放这里）
    conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Reaction conditions (T, P, potential, solvent, etc.)"
    )

    # 非物理元信息
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Source, label, author, notes"
    )

    created_at: Optional[str] = None


# =====================
# 数据存储
# =====================

# 确保数据写入项目根的 data/，无论从哪个工作目录启动服务
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # D:/chem_standard
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

REACTION_LOG = DATA_DIR / "reactions.jsonl"

SCHEMA_VERSION = "reaction.v1"


# =====================
# API
# =====================

@app.post("/upload_reaction")
def upload_reaction(payload: ReactionPayload):
    """
    接收 Reaction JSON，并以 jsonl 形式追加写入 data/reactions.jsonl
    """

    record = payload.model_dump()

    # ---- 系统字段（不可由用户指定）----
    record["reaction_id"] = str(uuid.uuid4())
    record["schema_version"] = SCHEMA_VERSION

    if record.get("created_at") is None:
        record["created_at"] = datetime.utcnow().isoformat() + "Z"

    try:
        with _write_lock:
            with REACTION_LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "ok",
        "reaction_id": record["reaction_id"],
        "logged_to": str(REACTION_LOG.resolve())
    }


# =====================
# 开发态启动
# =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "examples.api_reaction:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
