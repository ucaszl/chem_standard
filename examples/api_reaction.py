# examples/api_reaction.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from pathlib import Path
import json
import threading

# 浣跨敤鎴戜滑鏂扮殑瀹芥澗 schema
from chem_standard.io.api_schema import ReactionInput  # this is AtomInput / MoleculeInput / ReactionInput
from chem_standard.io.api_adapter import reactioninput_to_reaction, reaction_to_canonical_hash, is_duplicate, register_hash, write_reaction, REACTION_LOG

app = FastAPI(title="chem-standard Reaction API", version="0.3")

_write_lock = threading.Lock()
SCHEMA_VERSION = "reaction.v1"

@app.post("/upload_reaction")
def upload_reaction(payload: ReactionInput):
    """
    鎺ユ敹瀹芥澗 ReactionInput锛坋lement + x,y,z锛夛紝灏嗗叾鍗囩骇涓?core.Reaction锛?
    杩涜鍩烘湰鏍￠獙锛堜綅缃€佸厓绱犲畧鎭掞級锛屽幓閲嶅悗杩藉姞鍐欏叆 data/reactions.jsonl
    """
    try:
        r = reactioninput_to_reaction(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"input parsing error: {e}")

    # 鍩烘湰瀹堟亽妫€鏌?
    try:
        balanced = r.is_balanced()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"validation error: {e}")

    if not balanced:
        # 璁＄畻鍏冪礌宸€肩畝瑕佽鏄?
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

    # 鍘婚噸
    h = reaction_to_canonical_hash(r)
    if is_duplicate(h):
        # 鎵惧埌閲嶅锛氫笉鍐嶅啓鍏ワ紝浣嗚繑鍥炲凡瀛樺湪锛堣繖閲屾垜浠畝鍗曡繑鍥?duplicate true锛?
        return {"status": "ok", "duplicate": True, "hash": h, "logged_to": str(REACTION_LOG.resolve())}

    # 鍐欏叆
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

