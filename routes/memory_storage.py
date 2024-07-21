import os
from mem0 import Memory
from dotenv import load_dotenv

load_dotenv()

config = {
    "llm": {
        "provider": "groq",
        "config": {
            "model": "mixtral-8x7b-32768",
            "temperature": 0.1,
            "max_tokens": 1000,
        }
    }
}
memory_instanence = Memory.from_config(config)

