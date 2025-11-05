'''
I tried using OpenAI at first but it did not work great kept getting "insufficient_quota" type of error
tried everything even creating a new account, but it did not work
so I took the base of this project and used to develop "gemini.py" and it works great 
just needed a few changes on the payload variable witch I spent a lot of time to get it right :)
'''

import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx

load_dotenv()

KEY = os.getenv("OPENAI_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

app = FastAPI(title="PetLove API")

class Question(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

class Answer(BaseModel):
    response: str

@app.post("/api/question-and-answer", response_model=Answer)
async def q_and_a(req:Question):
    if not KEY:
        raise HTTPException(status_code=500, detail="Your API key is not configured")
    
    # writing sys message
    messages = [
        {
            "role": "system",
            "content": (
                "Você é o melhor assistente de vendas dentro de um e-comerce de pets de nome PetLove."
                "É crucial que você responda a cada pergunta de forma clara e educada. E quando você identificar o momento correto, suriga produtos do nosso catálogo (rações, acessórios e brinquedos)."
                "Quando for recomendar qualquer tipo de ração pergunte por mais informações como: idade e porte do animal assim como possíveis alergias."
            ),
        },
        {"role": "user", "content": req.question}
    ]

    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 500,
    }

    headers = {
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        gtp_resp = data.get("choices", [])[0].get("message", {}).get("content", "").strip()
        return {"response": gtp_resp}
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail={"error": "Erro de conexao", "info": e.response.text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok", "message": "POST /api/question-and-answer"}






