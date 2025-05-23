import io
import re
import pdfplumber
import faiss
import numpy as np
import langdetect

from googletrans import Translator
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from core.logging_logger import setup_logger
logger = setup_logger(__name__)

sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
translator = Translator()

def is_prompt_about_specific_table(prompt: str) -> str | None:
    match = re.search(r"(tabel\s+\d+)", prompt.lower()) or re.search(r"(table\s+\d+)", prompt.lower())
    return match.group(1) if match else None

def cleaning_text(text: str) -> str:
    text = text.replace("\n", " ").replace("\r", " ").strip()
    text = " ".join(text.split())
    return text

def extract_pdf_text_by_page(file_content) -> list:
    pages_text = []
    with pdfplumber.open(io.BytesIO(file_content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            tables = page.extract_tables()
            for table in tables:
                if table:
                    for row in table:
                        if row:
                            text += "\n" + " | ".join(cell if cell else "" for cell in row)
            pages_text.append(text.strip().lower())
    return pages_text

def find_pages_containing(pages: list, keyword: str) -> list:
    return [page for page in pages if keyword.lower() in page.lower()]

def find_relevant_chunks_with_faiss(texts: list, query: str, chunk_size: int = 500, top_k: int = 3) -> str:
    chunks = []

    query_lang_detect = langdetect.detect(query)
    texts_lang_detect = [langdetect.detect(text) for text in texts]
    texts_lang_detect_common = max(set(texts_lang_detect), key=texts_lang_detect.count)

    logger.info(f"Query language detected: {query_lang_detect}")
    logger.info(f"Texts language detected: {texts_lang_detect}")

    if query_lang_detect != texts_lang_detect_common:
        query = translator.translate(query, dest=texts_lang_detect_common).text
        logger.info(f"Translated query: {query}")

    for text in texts:  
        chunks.extend([text[i:i+chunk_size] for i in range(0, len(text), chunk_size)])

    chunk_embeddings = sentence_model.encode(chunks, normalize_embeddings=True).astype(np.float32)
    query_embeddings = sentence_model.encode([query], normalize_embeddings=True).astype(np.float32)

    logger.info(f"Chunk embeddings shape: {chunk_embeddings.shape}")
    logger.info(f"Query embedding shape: {query_embeddings.shape}")

    dim = chunk_embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  
    index.add(chunk_embeddings)

    logger.info(f"Index size: {index.ntotal}")
    
    distances, indices = index.search(query_embeddings, top_k)
    relevant_text = "\n\n".join([chunks[i] for i in indices[0]])
    return relevant_text

def find_relevant_chunks_with_cosim(texts: list, query: str, chunk_size: int = 500, top_k: int = 3) -> str:
    chunks = []

    query_lang_detect = langdetect.detect(query)
    texts_lang_detect = [langdetect.detect(text) for text in texts]
    texts_lang_detect_common = max(set(texts_lang_detect), key=texts_lang_detect.count)

    logger.info(f"Query language detected: {query_lang_detect}")
    logger.info(f"Texts language detected: {texts_lang_detect}")

    if query_lang_detect != texts_lang_detect_common:
        query = translator.translate(query, dest=texts_lang_detect_common).text
        logger.info(f"Translated query: {query}")

    for text in texts:
        chunks.extend([text[i:i+chunk_size] for i in range(0, len(text), chunk_size)])
    
    chunk_embeddings = sentence_model.encode(chunks)
    query_embedding = sentence_model.encode(query)

    similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]

    relevant_text = "\n\n".join([chunks[i] for i in top_indices])
    return relevant_text