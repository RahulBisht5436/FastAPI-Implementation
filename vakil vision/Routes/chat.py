from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from LLM.analyse import analyse_contract, chat_with_model
from LLM.config import settings
from LLM.vision import extract_text_from_image
from utils.extract import guess_image_media_type

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat(
    message: str = Form(...),
    image: UploadFile | None = File(None),
    mode: str = Form("analyze"),
    model: str | None = Form(None),
    vision_model: str | None = Form(None),
):
    """
    Multimodal chat endpoint.

    - analyze: structured contract analysis (default)
    - chat: free-form response using the reasoning model
    """
    try:
        context_parts: list[str] = []
        extracted_text: str | None = None

        if image and image.filename:
            image_bytes = await image.read()
            media_type = guess_image_media_type(image.filename, image.content_type)
            extracted_text = extract_text_from_image(
                image_bytes,
                media_type=media_type,
                model=vision_model,
            )
            context_parts.append(extracted_text)

        if message.strip():
            context_parts.append(message.strip())

        if not context_parts:
            raise HTTPException(status_code=400, detail="Message or image is required.")

        combined_context = "\n\n".join(context_parts)
        reasoning_model = model or settings.llm_model
        selected_vision_model = vision_model or settings.llm_vision_model

        if mode == "chat":
            reply = chat_with_model(message, combined_context, model=reasoning_model)
            return {
                "mode": "chat",
                "response": reply,
                "extracted_text": extracted_text,
                "model_used": reasoning_model,
                "vision_model_used": selected_vision_model if extracted_text else None,
            }

        analysis = analyse_contract(combined_context, model=reasoning_model)
        return {
            "mode": "analyze",
            "message": message,
            "extracted_text": extracted_text,
            "analysis": analysis,
            "model_used": reasoning_model,
            "vision_model_used": selected_vision_model if extracted_text else None,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}") from exc
