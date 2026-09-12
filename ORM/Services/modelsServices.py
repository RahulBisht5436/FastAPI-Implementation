from pydantic import BaseModel

class NewsArticle(BaseModel):
    title: str
    url: str
    summary: str
    published_date: str
    source: str
    author: str
    category: str
    tags: list[str]
    content: str
    image_url: str
    video_url: str
    audio_url: str
    sentiment: str
    sentiment_score: float
    sentiment_confidence: float
    sentiment_label: str
    sentiment_label_confidence: float
    sentiment_label_confidence: float