from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import os
import asyncio
from dotenv import load_dotenv
from aiohttp import ClientSession
from together import AsyncTogether, Together

from .query_llm import query_llm, QueryRequest
from .stream_request import stream_request, StreamingRequest
from .moa import run_llm, MoaRequest

load_dotenv()

router = APIRouter()

class CombinedRequest(BaseModel):
    question: str
    streaming_request: dict

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


@router.post("/combined")
async def combined_endpoint(request: CombinedRequest):
    question_string = request.question
    streaming_request_data = request.streaming_request

    async with ClientSession() as session:
        async_client = AsyncTogether(api_key=os.getenv("TOGETHER_API_KEY"), session=session)
        try:
            # Call query_llm endpoint
            llm_response = await query_llm(QueryRequest(question=question_string))
            llm_answer = llm_response['answer']

            # Call stream_request endpoint
            stream_response = await stream_request(StreamingRequest(**streaming_request_data))
            streaming_content = stream_response['response']

            # Run Mixture-of-Agents logic
            results = await asyncio.gather(*[run_llm(async_client, model, question_string) for model in reference_models])

            finalStream = client.chat.completions.create(
                model=aggregator_model,
                messages=[
                    {"role": "system", "content": aggregator_system_prompt},
                    {"role": "user", "content": ",".join(str(element) for element in results)},
                ],
                stream=True,
            )

            moa_content = ""
            for chunk in finalStream:
                moa_content += chunk.choices[0].delta.content or ""

            return {
                "llm_answer": llm_answer,
                "streaming_response": streaming_content,
                "moa_response": moa_content
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))