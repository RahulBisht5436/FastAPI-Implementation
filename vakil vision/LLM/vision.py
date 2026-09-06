import base64

from langchain_core.messages import HumanMessage

from LLM.factory import get_vision_llm

EXTRACTION_PROMPT = (
    "Extract all visible text from this image accurately. "
    "If it is a document or contract, preserve headings and structure. "
    "Return only the extracted text without commentary."
)


def extract_text_from_image(
    image_bytes: bytes,
    media_type: str = "image/jpeg",
    model: str | None = None,
) -> str:
    """Use a local vision model to OCR/describe uploaded image content."""
    llm = get_vision_llm(model)
    encoded = base64.b64encode(image_bytes).decode("utf-8")

    message = HumanMessage(
        content=[
            {"type": "text", "text": EXTRACTION_PROMPT},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{media_type};base64,{encoded}"},
            },
        ]
    )

    response = llm.invoke([message])
    return str(response.content)
