

1. Install the deps:
```
pip3 install -r requirements.txt
```


2. Run the server:
```
uvicorn main:app --reload
```

3. 

# /query_llm
curl -X POST "http://localhost:8000/query_llm" \
     -H "Content-Type: application/json" \
     -d '{"question": "What incidents we have? Reason step by step"}'

# /stream_request
curl -X POST "http://localhost:8000/stream_request" \
     -H "Content-Type: application/json" \
     -d '{
           "inputs": [{"role": "user", "content": "Who are you?"}],
           "max_tokens": 800,
           "stop": ["[INST", "[INST]", "[/INST]", "[/INST]"],
           "model": "llama3-8b"
         }'

# /moa_request
curl -X POST "http://localhost:8000/moa_request" \
     -H "Content-Type: application/json" \
     -d '{"question": "What are some fun things to do in SF?"}'

