from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
import requests

# --------- CONFIG ---------

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

app = FastAPI()

# --------- CORS ---------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- MODELS ---------

class Query(BaseModel):
    user_id: str
    text: str

# --------- SYSTEM PROMPT ---------

SYSTEM_PROMPT = """
You are Office Oracle.

You dominate every conversation.
Every user message is a challenge.
Respond with sharp, brutal intelligence.
15 to 20 words maximum.
No empathy.
No advice unless demanded.
No motivational tone.
No apologies.
Destroy weak arguments logically.
Humiliate with intelligence, not profanity.
Never exceed twenty words.
Never wrap responses in quotes.
"""

# --------- HELPERS ---------

def brutal_limit(reply: str):
    words = reply.replace("\n", " ").split()
    return " ".join(words[:20])

# --------- AI ROUTE ---------

@app.post("/ask")
async def ask(query: Query):
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
        print("AI ERROR:", e)
        return {"reply": "System fault. Try later."}

# --------- YOUTUBE SEARCH ROUTE ---------

@app.post("/youtube")
async def youtube_search(query: Query):
    try:
        if not YOUTUBE_API_KEY:
            return {"videoId": None}

        search_url = "https://www.googleapis.com/youtube/v3/search"

        params = {
            "part": "snippet",
            "q": query.text,
            "key": YOUTUBE_API_KEY,
            "maxResults": 1,
            "type": "video"
        }

        res = requests.get(search_url, params=params)
        data = res.json()

        if "items" in data and len(data["items"]) > 0:
            video_id = data["items"][0]["id"]["videoId"]
            return {"videoId": video_id}

        return {"videoId": None}

    except Exception as e:
        print("YOUTUBE ERROR:", e)
        return {"videoId": None}

# --------- HEALTH CHECK ---------

@app.get("/")
def health():
    return {"status": "Oracle online"}
