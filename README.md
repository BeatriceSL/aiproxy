# For use case

https://github.com/lukehollis/ai-murder-mystery-hackathon

1. Install the deps:
```
pip3 install -r requirements.txt
```


2. Run the server:
```
uvicorn main:app --reload
```

3. Call /query_llm
```
curl -X POST "http://localhost:8000/query_llm" \
     -H "Content-Type: application/json" \
     -d '{"question": "What incidents we have? Reason step by step"}'
```

4. Call /stream_request
```
curl -X POST "http://localhost:8000/stream_request" \
     -H "Content-Type: application/json" \
     -d '{
           "inputs": [{"role": "user", "content": "Who are you?"}],
           "max_tokens": 800,
           "stop": ["[INST", "[INST]", "[/INST]", "[/INST]"],
           "model": "llama3-8b"
         }'
```
5. Call MoA:
```
curl -X POST "http://localhost:8000/moa_request" \
     -H "Content-Type: application/json" \
     -d '{"question": "What are some fun things to do in SF?"}'
```

7. Call RAG stack /groq_query
```
curl -X POST "http://localhost:8000/groq_query" \
     -H "Content-Type: application/json" \
     -d '{
           "prompt_text": "What are some fun things to do in SF?"
         }'
```

7. /llamaindex_query
```
curl -X POST "http://localhost:8000/llamaindex_query" \
     -H "Content-Type: application/json"
```

8. Call All at once:
```
curl -X POST "http://localhost:8000/combined" \
     -H "Content-Type: application/json" \
     -d '{
           "inputs": [{"role": "user", "content": "Who are you?"}],
           "max_tokens": 800,
           "stop": ["[INST", "[INST]", "[/INST]", "[/INST]"],
           "model": "llama3-8b"
         }'
```
