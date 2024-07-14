from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import textgrad as tg
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/query_llm")
async def query_llm(request: QueryRequest):
    """
    Endpoint to query the LLM with a given question and return the LLM's answer.

    Args:
        request (QueryRequest): The request object containing the question.

    Returns:
        dict: A dictionary with the answer from the LLM.

    Raises:
        HTTPException: If there is an error during the query.
    """
    # Extract the question from the request
    question_string = request.question

    try:
        # Initialize the LLM engine and model
        llm_engine = tg.get_engine("gpt-3.5-turbo")
        tg.set_backward_engine("gpt-4o", override=True)
        model = tg.BlackboxLLM("gpt-4o")

        # Create a variable for the question and set its role description
        question = tg.Variable(question_string,
                               role_description="question to the LLM",
                               requires_grad=False)

        # Get the answer from the model
        answer = model(question)

        # Set the role description for the answer
        answer.set_role_description("concise and accurate answer to the question")

        # Create an optimizer and a loss function
        optimizer = tg.TGD(parameters=[answer])
        evaluation_instruction = (f"Here's a question: {question_string}. "
                                  "Evaluate any given answer to this question, "
                                  "be smart, logical, and very critical. "
                                  "Just provide concise feedback.")
        loss_fn = tg.TextLoss(evaluation_instruction)

        # Compute the loss and perform the backward pass
        loss = loss_fn(answer)
        loss.backward()

        # Update the answer
        optimizer.step()

        # Return the answer
        return {"answer": str(answer)}

    except Exception as e:
        # Raise an HTTPException if there is an error
        raise HTTPException(status_code=500, detail=str(e))
