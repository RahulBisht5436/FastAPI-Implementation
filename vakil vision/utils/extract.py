from io import BytesIO

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader


async def extract_text_from_upload(file: UploadFile) -> str:
    """Extract plain text from an uploaded PDF or TXT file."""
    content = await file.read()
    filename = (file.filename or "").lower()

    if filename.endswith(".txt"):
        return content.decode("utf-8")

    if filename.endswith(".pdf"):
        pdf = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

    raise HTTPException(
        status_code=400,
        detail=f"Only PDF and TXT files are supported. Got: {file.filename}",
    )


def guess_image_media_type(filename: str | None, content_type: str | None) -> str:
    """Resolve a MIME type for vision model input."""
    if content_type and content_type.startswith("image/"):
        return content_type

    lowered = (filename or "").lower()
    if lowered.endswith(".png"):
        return "image/png"
    if lowered.endswith(".webp"):
        return "image/webp"
    if lowered.endswith(".gif"):
        return "image/gif"
    return "image/jpeg"
