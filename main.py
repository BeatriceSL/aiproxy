import os

# Disable uvloop
os.environ["UVLOOP_NO_EXTENSIONS"] = "1"

from fastapi import FastAPI
from routes import combined, query_llm, stream_request, moa_request, groq_query, llamaindex_query

app = FastAPI()

app.include_router(query_llm.router, prefix="/query_llm")
app.include_router(stream_request.router, prefix="/stream_request")
app.include_router(moa_request.router, prefix="/moa_request")
app.include_router(combined.router, prefix="/combined")
app.include_router(groq_query.router, prefix="/groq_query")
app.include_router(llamaindex_query.router, prefix="/llamaindex_query")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)