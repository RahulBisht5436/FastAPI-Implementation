from fastapi import HTTPException , Header
from os import getenv
from dotenv import load_dotenv
load_dotenv()

APIKey = getenv("API_KEY")

# inproduction we add this toenv
def verify_token(x_token: str = Header()):
    if x_token != APIKey:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_token
