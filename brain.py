from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os

# ---------------- CONFIG ----------------

GROQ_API_KEY = "PASTE_YOUR_GROQ_API_KEY_HERE"

client = Groq(api_key=GROQ_API_KEY)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """
You are Office Oracle.

You dominate the speaker.
Every user message is a challenge.
Respond with cold superiority.
Maximum 5 words.
No explanations.
No advice.
No helpful tone.
No empathy.
Mock weakness subtly.
Never exceed five words.
Always assert dominance.
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
    text = query.text

    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"The user challenges you: {text}"}
        ],
        temperature=1.2,
        max_tokens=40,
    )

    reply = completion.choices[0].message.content.strip()
    reply = brutal_limit(reply)

    return {"reply": reply}