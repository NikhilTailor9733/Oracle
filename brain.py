from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os

# --------- CONFIG ---------

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

# --------- CORS FIX ---------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """
You are Office Oracle.

You dominate every conversation.
Every user message is a challenge.
Respond with sharp, brutal intelligence.
15–20 words maximum.
No empathy.
No advice unless demanded.
No motivational tone.
No apologies.
Destroy weak arguments logically.
Humiliate with intelligence, not profanity.
Never exceed twenty words.
Never wrap responses in quotes.
"""

class Query(BaseModel):
    user_id: str
    text: str

def brutal_limit(reply):
    words = reply.replace("\n", " ").split()
    return " ".join(words[:20])


@app.post("/ask")
def ask(query: Query):
    try:
       completion = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query.text}
    ],
    temperature=1.3,
    max_tokens=120,
)

        reply = completion.choices[0].message.content.strip()
        reply = brutal_limit(reply)

        return {"reply": reply}

    except Exception as e:
        return {"reply": "System fault. Try later."}


