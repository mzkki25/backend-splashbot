from fastapi import FastAPI
from pydantic import BaseModel
from core.gemini import model

import requests
import re
import random

GCS_API_KEY = "AIzaSyAmkMhuEWQL1X_1vSYePOIMmBSThnts3Oc"
GCS_CX = "83d930d4bd6364205"

app = FastAPI()

class QuestionRequest(BaseModel):
    question: str

class FollowUpRequest(BaseModel):
    question: str
    answer: str

class InitialQuestionsResponse(BaseModel):
    questions: list[str]

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question
    snippets = search_web_snippets(question)
    answer = generate_answer_with_context(question, snippets)
    journals = search_web_snippets(question, 3)
    return {
        "answer": answer,
        "journals": [{
            "title" : j.splitlines()[0], 
            "link"  : j.splitlines()[1], 
            "description"   : j.splitlines()[2]
        } for j in journals]
    }

@app.post("/follow_up")
async def follow_up_questions(request: FollowUpRequest):
    follow_up = recommend_follow_up_questions(request.question, request.answer)
    return {"follow_up": follow_up}

@app.get("/initial_questions", response_model=InitialQuestionsResponse)
async def initial_questions():
    questions = recommend_initial_questions()
    return {"questions": questions}

def search_web_snippets(query, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GCS_API_KEY,
        "cx": GCS_CX,
        "q": query,
        "num": num_results,
    }
    
    response = requests.get(url, params=params).json()
    results = []
    
    for item in response.get("items", []):
        title   = item.get("title", "No Title")
        link    = item.get("link", "")
        snippet = item.get("snippet", "")
        results.append(f"{title}\n{link}\n{snippet}")

    num_to_return = random.randint(1, min(5, len(results)))
    return random.sample(results, num_to_return)

def generate_answer_with_context(question, context_snippets):
    context = "\n".join(context_snippets)
    prompt = f"""
    Kamu adalah analis ekonomi. Berdasarkan informasi berikut dari internet, jawab pertanyaan ini secara ringkas dan akurat.

    === Informasi dari internet ===
    {context}

    === Pertanyaan ===
    {question}

    Jawab dengan gaya profesional.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def recommend_follow_up_questions(question, answer):
    prompt = f"""
    Berdasarkan pertanyaan berikut:

    "{question}"

    dan jawaban ini:

    "{answer}"

    Buat 3 pertanyaan lanjutan yang relevan dan profesional.
    """
    response = model.generate_content(prompt)
    return response.text.strip().split('\n')

def recommend_initial_questions():
    prompt = """
    Berikan 3 contoh pertanyaan penting terkait topik makroekonomi global yang cocok untuk ditanyakan ke chatbot analis ekonomi. Buatlah padat dan relevan dengan isu dunia saat ini.
    """
    response = model.generate_content(prompt)
    text = response.text.strip()
    lines = text.split('\n')
    questions = []
    for line in lines:
        line = line.strip()
        if line:
            line = re.sub(r'^\s*\d+[\.\)]\s*', '', line)
            questions.append(line)
    return questions[:4]
