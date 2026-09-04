# Import FastAPI and the required classes/functions for handling API requests,
# query parameters, and HTTP exceptions.
from fastapi import FastAPI, Request, Query, HTTPException

# Import the Pydantic models used to validate the menu item and API response structure.
from Models.data import MenuItem, MenuResponse

# Import the menu data from the Data module and give it a shorter local name.
from Data.data import menu_items as item_list


# Create the FastAPI application instance.
app = FastAPI(
    # Title displayed in the automatically generated API documentation.
    title="REST API request and response",

    # Description displayed in the API documentation.
    description="""
    this is the description for the project
     """
)


# Define the root/home endpoint.
# This endpoint is used to check whether the API is running.
@app.get("/")
def homeRouter():

    # Return a simple health/status response.
    return {
        "status": "healthysdaassdasd"
    }


# Define the GET /menu endpoint.
# response_model ensures that the returned response follows the MenuResponse model.
@app.get("/menu", response_model=MenuResponse)
def get_menu(
    # Define an optional query parameter named "category".
    # If category is not provided, its value will be None.
    category: str | None = Query(
        None,
        description="This is for the Query Response"
    )
):

    # Print the received category value in the terminal.
    print(category)

    # Print the complete menu list in the terminal for debugging.
    print(item_list)

    # Initially use the complete menu list.
    listItem = item_list

    # Check whether the user provided a category query parameter.
    if category:

        # Filter the menu items based on the requested category.
        # lower() is used on both values so the comparison is case-insensitive.
        listItem = [
            item for item in item_list
            if item["category"].lower() == category.lower()
        ]

        # If no items match the requested category,
        # return a 404 Not Found HTTP error.
        if not listItem:
            raise HTTPException(
                # HTTP 404 means the requested resource/data was not found.
                status_code=404,

                # Provide a useful error message to the API client.
                detail=f"No items found for category: {category}"
            )

    # Return the final response containing:
    # - status: indicates whether the request was successful
    # - count: number of items returned
    # - items: the actual menu items
    return {
        "status": "success",
        "count": len(listItem),
        "items": listItem
    }



@app.get("/menu/{orderId}",response_model=MenuItem)
def getOrder(orderId:int):
    print("Right function triggered===============>>>>>")
    for item in item_list:
        if item["id"] == orderId: 
            return item
        
    raise HTTPException(
                # HTTP 404 means the requested resource/data was not found.
                status_code=404,

                # Provide a useful error message to the API client.
                detail=f"No item found with ID: {orderId}"
            )
   