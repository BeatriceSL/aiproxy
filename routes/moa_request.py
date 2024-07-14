from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
import os
from together import AsyncTogether, Together
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class MoaRequest(BaseModel):
    user_prompt: str

client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

reference_models = [
    "Qwen/Qwen2-72B-Instruct",
    "Qwen/Qwen1.5-72B-Chat",
    "mistralai/Mixtral-8x22B-Instruct-v0.1",
    "databricks/dbrx-instruct",
]
aggregator_model = "mistralai/Mixtral-8x22B-Instruct-v0.1"
aggregator_system_prompt = """You have been provided with a set of responses from various open-source models to the latest user query. Your task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the information provided in these responses, recognizing that some of it may be biased or incorrect. Your response should not simply replicate the given answers but should offer a refined, accurate, and comprehensive reply to the instruction. Ensure your response is well-structured, coherent, and adheres to the highest standards of accuracy and reliability.

Responses from models:"""


async def run_llm(async_client, model, user_prompt):
    """Run a single LLM call with a reference model."""
    response = await async_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": user_prompt}],
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content


@router.post("/moa_request")
async def moa_request(request: MoaRequest):
    user_prompt = request.user_prompt
    async_client = AsyncTogether(api_key=os.getenv("TOGETHER_API_KEY"))

    try:
        results = await asyncio.gather(*[run_llm(async_client, model, user_prompt) for model in reference_models])

        finalStream = client.chat.completions.create(
            model=aggregator_model,
            messages=[
                {"role": "system", "content": aggregator_system_prompt},
                {"role": "user", "content": ",".join(str(element) for element in results)},
            ],
            stream=True,
        )

        content = ""
        for chunk in finalStream:
            content += chunk.choices[0].delta.content or ""

        return {"response": content}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))