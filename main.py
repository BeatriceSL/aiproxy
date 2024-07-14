from fastapi import FastAPI
from routes import query_llm, stream_request, moa_request

app = FastAPI()

app.include_router(query_llm.router)
app.include_router(stream_request.router)
app.include_router(moa_request.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)