# Contract upload routes: accept PDF/TXT files, extract text, and run AI analysis.
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from LLM.analyse import analyse_contract
from utils.extract import extract_text_from_upload

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("/upload")
async def upload_contract(
    file: UploadFile = File(...),
    model: str | None = Form(None),
):
    """Upload a contract file and return structured AI analysis."""
    try:
        text = await extract_text_from_upload(file)
        analysis = analyse_contract(text, model=model)
        return analysis

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {exc}",
        ) from exc
