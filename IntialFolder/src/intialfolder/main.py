from fastapi import FastAPI
from fastapi import Request

app = FastAPI(
    title="Test Project",
    description="This is a test project",
    version="1.0.0",
    openapi_url="/openapi.json"
)


@app.get("/")
def homeRoute():
    """Root EndPoint - Basic Health Check """
    print("You have hitted the basic Route")
    return {
        "message":"this is the basic route",
        "status":"Healthy"
    }
    
@app.get(
    "/orders",
    summary="this endpoint gives the orders",
    description="""these are dummy description """,
    tags=["order","require authentication"],
    response_description="List all the orders",
    deprecated=False
    )
def homeRoute():
    print("You have hitted the order Route")
    return {
        "orderid":"123",
        "orders":[
            {
                "suborderid":123,
                "order_description":"this is random description",
                "order_items":["patato","chips"]
             },
            {
                "suborderid":234,
                "order_description":"this is random description 2",
                "order_items":["patato 2","chips 2"]
             }
        ]
    }



@app.get("/debug/request")
async def request_api(request: Request):

    print("\n========== FULL REQUEST ==========")

    # HTTP method
    print("METHOD:", request.method)

    # Full URL
    print("URL:", request.url)

    # Headers
    print("\nHEADERS:")
    print(dict(request.headers))

    # Query parameters
    print("\nQUERY PARAMETERS:")
    print(dict(request.query_params))

    # Path parameters
    print("\nPATH PARAMETERS:")
    print(request.path_params)

    # Cookies
    print("\nCOOKIES:")
    print(request.cookies)

    # Client information
    print("\nCLIENT:")
    print(request.client)

    # Body
    body = await request.body()

    print("\nBODY:")
    print(body)

    print("=================================\n")

    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "path_params": request.path_params,
        "cookies": request.cookies,
        "body": body.decode("utf-8", errors="replace")
    }