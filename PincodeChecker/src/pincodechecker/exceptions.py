from fastapi.responses import JSONResponse
from fastapi import Request


# ============================================================
# Custom exceptions for pincode-related errors
#
# These are raised in route handlers (main.py) when something
# goes wrong. FastAPI does NOT handle them automatically —
# we register handlers below via app.add_exception_handler().
# ============================================================


class PincodeNotFoundError(Exception):
    """
    Raised when the pincode format is valid (6 digits) but
    no matching location exists in the pincodes dataset.

    Example: "999999" is a valid format but not in our data.
    """

    def __init__(self, pincode: str):
        self.pincode = pincode


class InvalidPincode(Exception):
    """
    Raised when the pincode fails format validation
    (not 6 digits, contains letters, etc.).

    Example: "12345" (too short) or "12A456" (contains a letter).
    """

    def __init__(self, pincode: str, reason: str = "Invalid Format"):
        self.pincode = pincode
        self.reason = reason


# ============================================================
# Exception handlers
#
# Each handler converts a custom exception into a JSON response.
# Registered in main.py:
#   app.add_exception_handler(PincodeNotFoundError, pincode_not_found_handler)
#   app.add_exception_handler(InvalidPincode, invalid_pincode)
# ============================================================


async def pincode_not_found_handler(request: Request, exc: PincodeNotFoundError):
    # request: the incoming HTTP request (required by FastAPI's handler signature)
    # exc: the PincodeNotFoundError instance that was raised
    return JSONResponse(
        status_code=404,
        content={
            "error": "pincode_not_found",
            "message": f"No Location for pincode : {exc.pincode}",
        },
    )


async def invalid_pincode(request: Request, exc: InvalidPincode):
    # request: the incoming HTTP request (required by FastAPI's handler signature)
    # exc: the InvalidPincode instance that was raised
    return JSONResponse(
        status_code=404,
        content={
            "error": "Invalid Pincode",
            "message": f"Invalid pincode : {exc.pincode} because {exc.reason}",
        },
    )
