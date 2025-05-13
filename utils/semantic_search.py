import pdfplumber
import io

from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

def cleaning_text(text: str) -> str:
    text = text.replace("\n", " ").replace("\r", " ").strip()
    text = " ".join(text.split())
    return text

def extract_pdf_text_and_tables_from_blob(file_content) -> str:
    with pdfplumber.open(io.BytesIO(file_content)) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text() or ""
            text = cleaning_text(text)
            full_text += text + " "

            tables = page.extract_tables()
            for table in tables:
                if table:  
                    for row in table:
                        if row:
                            full_text += " | ".join(cell if cell else "" for cell in row) + " "
    return full_text.strip()

def extract_pdf_image_from_blob(file_content) -> str:
    with pdfplumber.open(io.BytesIO(file_content)) as pdf:
        images = []
        for page in pdf.pages:
            for img in page.images:
                x0, y0, x1, y1 = img['x0'], img['top'], img['x1'], img['bottom']
                cropped_image = page.within_bbox((x0, y0, x1, y1)).to_image()
                images.append(cropped_image)
    return images

def find_relevant_chunks(text: str, query: str, chunk_size: int = 500, top_k: int = 3) -> str:
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    # relevant_text = " ".join(chunks[:top_k])  
    
    chunk_embeddings = sentence_model.encode(chunks)
    query_embedding = sentence_model.encode(query)

    similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]

    relevant_text = " ".join([chunks[i] for i in top_indices])

    return relevant_text