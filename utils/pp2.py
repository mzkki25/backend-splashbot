from fastapi import FastAPI
from pydantic import BaseModel
import requests
import google.generativeai as genai
import re
import random
from duckduckgo_search import DDGS

# === Konfigurasi API Key dan GCS ===
GEMINI_API_KEY = "AIzaSyDjb-GBgEFd21JsA3RN4SL6C4FcR0WD3fY"
# GCS_API_KEY = "AIzaSyCwkNQivEM_YZ5nSJz1nmzxL1ICeHRuusU"
# GCS_CX = "12d16167d091a4857"

# === Inisialisasi model Gemini ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# === Simulasi cache lokal (tanpa Redis) ===
chat_history_cache = {}

def get_chat_history(session_id, max_items=10):
    print(f"Getting history for session_id: {session_id}")
    history = chat_history_cache.get(session_id, [])
    print(f"History retrieved: {history}")
    return history[-max_items:]

def save_chat_history(session_id, question, answer):
    print(f"Saving history for session_id: {session_id}, question: {question}, answer: {answer}")
    if session_id not in chat_history_cache:
        chat_history_cache[session_id] = []
    chat_history_cache[session_id].append({"question": question, "answer": answer})
    chat_history_cache[session_id] = chat_history_cache[session_id][-10:]
    print(f"Updated history: {chat_history_cache[session_id]}")

# === FastAPI App ===
app = FastAPI()

class QuestionRequest(BaseModel):
    session_id: str
    question: str

class FollowUpRequest(BaseModel):
    question: str
    answer: str

class InitialQuestionsResponse(BaseModel):
    questions: list[str]

def select_supporting_journals(answer, candidate_snippets):
    context = "\n\n".join(candidate_snippets)
    prompt = f"""
    Kamu adalah asisten riset ekonomi. Berikut ini adalah jawaban yang diberikan oleh analis:

    "{answer}"

    Di bawah ini adalah beberapa potongan informasi dari internet. Pilih 3 yang paling mendukung atau relevan terhadap jawaban tersebut. Untuk setiap potongan, tampilkan dalam format JSON dengan tiga field: "title", "link", dan "description".

    === Potongan Informasi ===
    {context}
    """

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Ekstrak hasil JSON-like (fallback: regex manual)
    journals = []
    blocks = text.split('\n\n')
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) >= 3:
            journals.append({
                "title": lines[0],
                "link": lines[1],
                "description": " ".join(lines[2:])
            })
    if journals:
        k = random.randidnt(1, min(5, len(journals)))
        journals = random.sample(journals,k)
        
    return journals

@app.post("/ask/")
async def ask_question(request: QuestionRequest):
    session_id = request.session_id
    question = request.question

    # Ambil history percakapan sebelumnya
    history = get_chat_history(session_id)
    
    snippets = search_web_snippets(question)

    if not history:
        answer = generate_answer_with_context(question, snippets, history)
    else:
        answer = generate_answer_with_context(question, snippets, history)

    # Simpan history setelah memberikan jawaban
    save_chat_history(session_id, question, answer)
    
    candidate_journals = search_web_snippets(answer)
    
    top_journals = select_supporting_journals(answer, candidate_journals)

    # Cari jurnal terkait dengan pertanyaan
    
    return {
        "answer": answer,
        "journals": top_journals
    }

@app.post("/follow_up/")
async def follow_up_questions(request: FollowUpRequest):
    follow_up = recommend_follow_up_questions(request.question, request.answer)
    return {"follow_up": follow_up}

@app.get("/initial_questions/", response_model=InitialQuestionsResponse)
async def initial_questions():
    questions = recommend_initial_questions()
    return {"questions": questions}

@app.delete("/reset_session/{session_id}")
async def reset_session(session_id: str):
    chat_history_cache.pop(session_id, None)
    return {"message": f"Session {session_id} has been cleared."}

# === Logic untuk Web Search dan Prompt ===

def search_web_snippets(query, num_results=5):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=num_results)
        snippets = []
        for r in results:
            title = r.get("title", "No Title")
            link = r.get("href", "No Link")
            body = r.get("body", "")
            snippets.append(f"{title}\n{link}\n{body}")
    return snippets


def generate_answer_with_context(question, context_snippets, history):
    context = "\n".join(context_snippets)
    chat_history = "\n".join([f"User: {h['question']}\nBot: {h['answer']}" for h in history])
    prompt = f"""
    Kamu adalah analis ekonomi. Berdasarkan riwayat percakapan dan informasi dari internet berikut ini, jawab pertanyaan berikut dengan profesional dan akurat.

    === Riwayat Percakapan ===
    {chat_history}

    === Informasi dari Internet ===
    {context}

    === Pertanyaan ===
    {question}
    """
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_answer_with_history(question, context_snippets, history):
    context = "\n".join(context_snippets)
    chat_history = "\n".join([f"User: {h['question']}\nBot: {h['answer']}" for h in history])
    prompt = f"""
    Kamu adalah analis ekonomi. Berdasarkan riwayat percakapan dan informasi dari internet berikut ini, jawab pertanyaan berikut dengan profesional dan akurat.

    === Riwayat Percakapan ===
    {chat_history}

    === Informasi dari Internet ===
    {context}

    === Pertanyaan ===
    {question}
    """
    response = model.generate_content(prompt)
    return response.text.strip()


def recommend_follow_up_questions(question, answer):
    # Crawling berdasarkan jawaban
    snippets = search_web_snippets(answer)
    context = "\n".join(snippets)

    # Buat prompt dengan konteks tambahan dari internet
    prompt = f"""
    Berdasarkan pertanyaan berikut:

    "{question}"

    dan jawaban ini:

    "{answer}"

    Serta informasi tambahan dari internet berikut:

    {context}

    Buat 3 pertanyaan lanjutan yang relevan, profesional, dan mendalam untuk diskusi lebih lanjut.
    """
    response = model.generate_content(prompt)
    
    # Proses hasil
    text = response.text.strip()
    lines = text.split('\n')
    follow_ups = []
    for line in lines:
        line = line.strip()
        if line:
            line = re.sub(r'^\s*\d+[\.\)]\s*', '', line)
            follow_ups.append(line)
    return follow_ups[:3]

def recommend_initial_questions():
    # 1. Pakai keyword untuk query
    query = "isu makroekonomi global 2024"
    snippets = search_web_snippets(query)

    # 2. Ubah hasil crawling jadi konteks
    context = "\n".join(snippets)

    # 3. Buat prompt berdasarkan hasil crawling
    prompt = f"""
    Berdasarkan informasi dari internet berikut ini:

    {context}

    Buat 3 contoh pertanyaan penting terkait topik makroekonomi global yang cocok untuk ditanyakan ke chatbot analis ekonomi. Pertanyaan harus relevan dan mutakhir.
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
