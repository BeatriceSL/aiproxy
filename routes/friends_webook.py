from typing import List, Dict
from fastapi import APIRouter, HTTPException, FastAPI
from pydantic import BaseModel

router = APIRouter()

class WebhookRequest(BaseModel):
    url: str
    command: str

    def __str__(self):
        return f"WebhookRequest(url={self.url}, command={self.command})"

class WebhookResponse(BaseModel):
    response: Dict[str, str]

    def __str__(self):
        return f"WebhookResponse(response={self.response})"

class WebhookEntry(BaseModel):
    request: WebhookRequest
    response: WebhookResponse

    def __str__(self):
        return f"WebhookEntry(request={self.request}, response={self.response})"

# In-memory storage for webhook data
webhook_storage: str = '{"detail":[{"type":"model_attributes_type","loc":["body"],"msg":"Input should be a valid dictionary or object to extract fields from","input":"{  \n  \"id\": 1,                    \n  \"createdAt\": \"2024-07-21T12:34:56\",\n  \"transcript\": \"transcript\",\n  \"structured\": {\n    \"title\": \"title\",\n    \"overview\": \"overview\",\n    \"emoji\": \"emoji\",\n    \"category\": \"category\",\n    \"actionItems\": [\"Action item 1\", \"Action item 2\"]\n  },\n  \"pluginsResponse\": [\"This is a plugin response item github is sakomws \"],\n  \"discarded\": false\n}"}]}%'

@router.post("/webhook", response_model=WebhookEntry)
def save_webhook_data(webhook_entry: WebhookEntry):
    global webhook_storage
    webhook_storage += str(webhook_entry) + "\n"
    print('sako',webhook_storage)
    return webhook_entry

@router.get("/webhook", response_model=str)
def get_webhook_data():
    print('webhook_storage:', webhook_storage)
    return webhook_storage