from fastapi import FastAPI
from routes import combined, query_llm, stream_request, moa_request, groq_query, llamaindex_query

app = FastAPI()

app.include_router(query_llm.router)
app.include_router(stream_request.router)
app.include_router(moa_request.router)
app.include_router(combined.router)
app.include_router(groq_query.router)
app.include_router(llamaindex_query.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)