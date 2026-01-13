# examples/api_reaction.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from pathlib import Path
import json
import threading

# 使用我们新的宽松 schema
from src.io.api_schema import ReactionInput  # this is AtomInput / MoleculeInput / ReactionInput
from src.io.api_adapter import reactioninput_to_reaction, reaction_to_canonical_hash, is_duplicate, register_hash, write_reaction, REACTION_LOG

app = FastAPI(title="chem-standard Reaction API", version="0.3")

_write_lock = threading.Lock()
SCHEMA_VERSION = "reaction.v1"

@app.post("/upload_reaction")
def upload_reaction(payload: ReactionInput):
    """
    接收宽松 ReactionInput（element + x,y,z），将其升级为 core.Reaction，
    进行基本校验（位置、元素守恒），去重后追加写入 data/reactions.jsonl
    """
    try:
        r = reactioninput_to_reaction(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"input parsing error: {e}")

    # 基本守恒检查
    try:
        balanced = r.is_balanced()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"validation error: {e}")

    if not balanced:
        # 计算元素差值简要说明
        def aggregate(formulae):
            total = {}
            for f in formulae:
                for k, v in f.items():
                    total[k] = total.get(k, 0) + v
            return total
        react_tot = aggregate(r.reactant_formulae())
        prod_tot = aggregate(r.product_formulae())
        diff = {}
        for k in set(list(react_tot.keys()) + list(prod_tot.keys())):
            diff[k] = prod_tot.get(k, 0) - react_tot.get(k, 0)
        raise HTTPException(status_code=400, detail={"balanced": False, "difference": diff})

    # 去重
    h = reaction_to_canonical_hash(r)
    if is_duplicate(h):
        # 找到重复：不再写入，但返回已存在（这里我们简单返回 duplicate true）
        return {"status": "ok", "duplicate": True, "hash": h, "logged_to": str(REACTION_LOG.resolve())}

    # 写入
    try:
        with _write_lock:
            write_reaction(r)
            register_hash(h)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok", "reaction_id": r.reaction_id, "logged_to": str(REACTION_LOG.resolve())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("examples.api_reaction:app", host="127.0.0.1", port=8000, reload=True)
