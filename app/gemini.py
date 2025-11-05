import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

app = FastAPI(title="PetLove API Test With Gemini")

class Question(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)

class Answer(BaseModel):
    response: str

@app.post("/api/question-and-answer", response_model=Answer)
async def q_and_a(req: Question):
    if not KEY:
        raise HTTPException(status_code=500, detail="API key do Gemini não configurada")

    