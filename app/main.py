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
    question: str = Field(..., min_c=1, max_c=2000)

class Response(BaseModel):
    response: str


