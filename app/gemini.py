import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

app = FastAPI(title="PetLove API Test With Gemini")

class Question(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

class Answer(BaseModel):
    response: str

@app.post("/api/question-and-answer", response_model=Answer)
async def q_and_a(req: Question):
    if not KEY:
        raise HTTPException(status_code=500, detail="API key do Gemini não configurada")

    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "Você é o melhor assistente de vendas dentro de um e-commerce de pets de nome PetLove. "
                        "Responda sempre de forma clara e educada. "
                        "Quando identificar o momento, sugira produtos do nosso catálogo "
                        "(rações, acessórios e brinquedos). "
                        "Para recomendar ração, peça informações como idade, porte e alergias."
                    )
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": req.question
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 800
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail={"error": "Erro de conexão Gemini", "info": e.response.text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        candidates = data.get("candidates", [])
        if not candidates:
            raise ValueError("Nenhuma resposta recebida do modelo")

        content = candidates[0].get("content", {})
        parts = content.get("parts")

        if not parts or not isinstance(parts, list):
            raise ValueError(f"A estrutura de resposta não é válida: {content}")
        
        text = parts[0].get("text", "")

        if not text:
            raise ValueError(f"Não há texto na resposta: {data}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao parsear resposta Gemini: {e}")
    
    return {"response": text.strip()}

@app.get("/")
async def root():
    return {"status": "ok", "message": "POST /api/question-and-answer"}