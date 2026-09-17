from fastapi import APIRouter, Request
from LLM.plannerTools import get_weather
planner_router = APIRouter(
    prefix="/plan",
    tags=["planner"],
)


# Need to understand inside the base Router can be have dependecy injected or not?
# code example : 
#     planner_router = APIRouter(
#     prefix="/plan",
#     tags=["planner"],
#     dependencies=[Depends(get_token_header)],
# )

@planner_router.post("/")
async def create_aggregated_plan(request: Request):
    """Aggregated Weather , Currency and Places into a single travel plan"""
    body = await request.json()
    city = body["city"]
    weather = get_weather.invoke({"city": city})
    
    return {
        "status": "success",
        "message": "Aggregated plan created successfully",
        "weather": weather,
    }



@planner_router.post("/health")
def health():
    return {
        "status": "healthy",
        "message": "Yatra Planner is running",
    }
    
    