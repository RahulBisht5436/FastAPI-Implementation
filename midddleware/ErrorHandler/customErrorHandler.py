from fastapi import Request
from fastapi.responses import JSONResponse

# Making the class for the Exception
class customException(Exception):
    # Here the Execption inheritied from Python Base model
    def __init__(self, message: str, errorCode: int, description: str):
        self.message = message
        self.errorCode = errorCode
        self.description = description
        super().__init__(message)

#Created the Exception Handler
async def handle_custom_exception(request: Request, exc: customException):
    return JSONResponse(
        status_code=exc.errorCode,
        content={
            "message": exc.message,
            "error_code": exc.errorCode,
            "description": exc.description,
        },
    )
