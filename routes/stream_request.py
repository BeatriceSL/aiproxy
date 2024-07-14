from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class StreamingRequest(BaseModel):
    inputs: List[dict]
    max_tokens: int
    stop: List[str]
    model: str

SAMBANOA_API_URL = os.getenv('SAMBANOA_API_URL')
SAMBANOA_API_KEY = os.getenv('SAMBANOA_API_KEY')

@router.post("/stream_request")
async def stream_request(request: StreamingRequest):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + SAMBANOA_API_KEY
    }

    response = requests.post(SAMBANOA_API_URL, headers=headers, json=request.dict(), stream=True)

    if response.status_code == 200:
        content = ""
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                content += chunk.decode('utf-8')
        return {"response": content}
    else:
        raise HTTPException(status_code=response.status_code, detail="Request failed")