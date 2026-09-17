from fastapi import APIRouter
from ErrorHandler.customErrorHandler import customException
route = APIRouter(
    prefix="/test",
    tags=["Users"]
)


@route.get("/testUsers")
def testUsers():
    raise customException("Nice to see u again" , 404 , "this is hidden message for u")
    return ["Alice", "Bob"]