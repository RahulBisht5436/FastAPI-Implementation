from fastapi import FastAPI , Request , Query
from Models.data import MenuItem , MenuResponse

app = FastAPI(
    title="REST API request and response",
    description="""
    this is the description for the project
     """
     
)

@app.get("/")
def homeRouter():
    return{
        "status":"healthy"
    }

@app.get("/menu", response_model=MenuResponse)
def get_menu(category:str | None = Query(None ,description="This is for the Query Response")):
    print(category)
    return {
        "status":"success",
        "count":1,
        "items":[
            {
            "id": 1,
            "name": "Masala Dosa",
            "category": "South Indian Food",
            "description": "Crispy dosa filled with spicy potato masala.",
            "price": 80,
            "available": True
         }
    ]
    }