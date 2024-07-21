from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from multion.client import MultiOn
import os
from dotenv import load_dotenv
import agentops
import requests

load_dotenv()

# agentops.init(os.getenv("AGENTOPS_API_KEY"))
multion_api_key = os.getenv("MULTION_API_KEY")
multion = MultiOn(api_key=multion_api_key)

router = APIRouter()

class Memory(BaseModel):
    url: str
    command: str

@router.post("/multion_webhook")
async def webhook(memory: Memory):
    try:
        if not multion_api_key:
            raise HTTPException(status_code=500, detail="API key not found.")
        
        # Perform the browse operation using MultiOn client
        browse = multion.browse(
            cmd=memory.command,
            url=memory.url,
            include_screenshot=True
        )
        
        # Fetch data from the /webhook endpoint
        response = requests.get("http://127.0.0.1:8000/webhook")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch webhook data.")
        
        webhook_data = response
        if not webhook_data:
            raise HTTPException(status_code=404, detail="No webhook data found.")
    
        print("Browse response:", browse)
        return {
            "webhook_data": webhook_data,
            "browse_response": browse
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))