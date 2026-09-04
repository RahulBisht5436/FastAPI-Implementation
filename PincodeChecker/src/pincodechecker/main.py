from fastapi import FastAPI
from pydantic_core.core_schema import custom_error_schema
from .exceptions import PincodeNotFoundError , InvalidPincode , pincode_not_found_handler, invalid_pincode
from Data.pincode import pincodes
from Models.pincode import BuldResponse ,BulkRequest ,LocationResponse ,PincodeRequest
from pydantic import ValidationError

app = FastAPI(
    title="Pincode Checker",
    description="This Folder gives you the address based on the pincode",
    openapi_external_docs="/opendoc"
)

# register customer handler 
app.add_exception_handler(PincodeNotFoundError,pincode_not_found_handler)
app.add_exception_handler(InvalidPincode, invalid_pincode)


@app.get("/")
def root():
    return {}

@app.get("/health")
def healthCheck():
    return {
        "message":"System is healthy",
        "code":200
    }
    
@app.get("/pincode/{code}", response_model=LocationResponse)
def location_handler(code:str ):
    
     # Step 1: validate format using PincodeRequest
    try:
        validated = PincodeRequest(pincode=code)
    except ValidationError:
        raise InvalidPincode(code, "Pincode must be exactly 6 digits")
    
    if code not in pincodes:
        raise PincodeNotFoundError(code)
    return pincodes[code]
    
@app.post("/pincodes", response_model=BuldResponse)
def handleBulkRequest(request: BulkRequest):
    foundPincode = 0
    notFoundPinCode = 0
    pincodeArray = []
    for pin in request.pincodes:
        if pin not in pincodes:
            notFoundPinCode += 1
        else:
            foundPincode += 1
            pincodeArray.append(pincodes[pin])
    return {
        "status": "success",
        "found": foundPincode,
        "not_found": notFoundPinCode,
        "pincodes": pincodeArray,
    }
    
    