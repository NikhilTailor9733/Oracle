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
You dominate the speaker.
Maximum 5 words.
Cold superiority only.
No explanations.
No empathy.
Never wrap responses in quotes.
"""

class Query(BaseModel):
    user_id: str
    text: str


def brutal_limit(reply):
    words = reply.replace("\n", " ").split()
    return " ".join(words[:5])


@app.post("/ask")
def ask(query: Query):
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query.text}
            ],
            temperature=1.2,
            max_tokens=40,
        )

        reply = completion.choices[0].message.content.strip()
        reply = brutal_limit(reply)

        return {"reply": reply}

    except Exception as e:
        return {"reply": "System fault. Try later."}
