from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

router = APIRouter()


class SummarizeRequest(BaseModel):
    text: str


@router.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "doc"}

@router.post("/summarize")
def summarize(req: SummarizeRequest):
    """Very small placeholder summarizer (no LLM)."""
    text = req.text or ""
    # naive summary: first 2 non-empty lines
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    summary = " ".join(lines[:2]) if lines else ""
    return {"summary": summary}

@router.post("/generate")
async def generate_docs(request: Dict):
    try:
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
