from fastapi import APIRouter , Depends , Query , Request
from Services.searchNewsService import search_news
from Utilities.JWTTokken import verify_access_token

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

@router.get("/" , dependencies=[Depends(verify_access_token)])
async def search_news_route(request: Request ):
    data = await request.json()
    news_query = data.get("query")
    return search_news(news_query)