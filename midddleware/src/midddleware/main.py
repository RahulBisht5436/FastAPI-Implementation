from fastapi import FastAPI, Request, HTTPException, Depends
from Routes.testingRoute1 import route as testRoute
from ErrorHandler.customErrorHandler import customException, handle_custom_exception
import random

app = FastAPI(
    title="Middle ware Implementation",
    description="This is the description of the middleware",
    docs_url="/docs",
    redoc_url="/redocs"
)

from ErrorHandler.customErrorHandler import customException, handle_custom_exception
app.add_exception_handler(customException, handle_custom_exception)


@app.middleware("http")
async def addcustomerHeader(request : Request , call_next):
    print("custom headers added")
    response = await call_next(request)
    print("after call execution")
    return response


app.include_router(testRoute)

def failedExecution():
    randomNumber = random.randint(1, 2)
    if(randomNumber // 2 == 0):
        raise HTTPException(400,"Failed through middleawre")
    return


@app.get("/test2",dependencies=[Depends(failedExecution)])
def printSecond():
    print("this is the second print")
    return None