from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from models.schemas import ChatRequest, ChatResponse

from core.firebase import db, bucket
from core.gemini import model, multimodal_model
from utils.semantic_search import find_relevant_chunks, extract_pdf_text_and_tables_from_blob
from utils.makroeconomics import (
    two_wheels_model, 
    four_wheels_model, 
    retail_general_model, 
    retail_beauty_model, 
    retail_fnb_model, 
    retail_drugstore_model
)
from api.deps import get_current_user
from PIL import Image
from firebase_admin import firestore
from datetime import datetime

import io

now = datetime.now()
router = APIRouter()

@router.post("/{chat_session}", response_model=ChatResponse)
async def process_chat(chat_session: str, chat_request: ChatRequest, user = Depends(get_current_user)):
    try:
        user_id = user['uid']
        prompt = chat_request.prompt
        file_id_input = chat_request.file_id
        file_url = None
        last_response = None

        chat_ref = db.collection('chats').document(chat_session)
        chat_doc = chat_ref.get()

        if not chat_doc.exists:
            chat_title = prompt[:30] + "..." if len(prompt) > 30 else prompt
            chat_ref.set({
                'user_id': user_id,
                'title': chat_title,
                'status': 'active',
                'messages': [],
                'created_at': firestore.SERVER_TIMESTAMP,
                'last_file_id': file_id_input if file_id_input else None,
                'last_response': None
            })
            last_file_id = file_id_input
        else:
            chat_data = chat_doc.to_dict()

            last_file_id = chat_data.get("last_file_id")
            last_response = chat_data.get("last_response")

            if file_id_input and file_id_input != last_file_id:
                chat_ref.update({'last_file_id': file_id_input})
                last_file_id = file_id_input

            elif not file_id_input and last_file_id:
                file_id_input = last_file_id

        if chat_request.chat_options == "General Macroeconomics":
            if file_id_input:
                file_doc = db.collection('files').document(file_id_input).get()
                if not file_doc.exists:
                    raise HTTPException(status_code=404, detail="File not found")

                file_data = file_doc.to_dict()
                file_url = file_data.get('url')
                content_type = file_data.get('content_type')
                storage_path = file_data.get('storage_path')

                blob = bucket.blob(storage_path)
                file_content = blob.download_as_bytes()

                if 'application/pdf' in content_type:
                    pdf_text = extract_pdf_text_and_tables_from_blob(file_content)

                    if len(pdf_text) > 1000:
                        relevant_text = find_relevant_chunks(
                            text=pdf_text, 
                            query=prompt, 
                            chunk_size=650, 
                            top_k=5
                        )
                    else:
                        relevant_text = pdf_text

                    response = model.generate_content(
                        f"""
                        Kamu adalah SPLASHBot yang mengkhususkan diri dalam ekonomi dan menganalisis PDF yang diberikan.\\n\n
                        Konten PDF: {relevant_text}\n\n
                        Pertanyaan dari user: {prompt}
                        Apabila PDF yang diberikan bukan berkaitan dengan ekonomi, mohon untuk tidak menjawab.\n\n
                        Bold lah kata kunci yang penting dalam jawaban.\n\n
                        """
                    ).text

                elif content_type.startswith('image/'):
                    image = Image.open(io.BytesIO(file_content)).convert("RGB")

                    response = multimodal_model.generate_content(
                        [
                            """
                            Kamu adalah SPLASHBot yang mengkhususkan diri dalam ekonomi dan menganalisis gambar yang diberikan.
                            """,
                            image,
                            f"""
                            Pertanyaan dari user: {prompt}
                            Apabila gambar yang diberikan bukan berkaitan dengan ekonomi, mohon untuk tidak menjawab.\n\n
                            Bold lah kata kunci yang penting dalam jawaban.\n\n
                            """
                        ]
                    ).text
                else:
                    raise HTTPException(status_code=400, detail="Unsupported file type")

            else:
                response = model.generate_content(
                    f"""
                        Kamu adalah SPLASHBot yang mengkhususkan diri dalam menjawab pertanyaan seputar ekonomi.\n\n
                        Pertanyaan dari user: {prompt}
                        Selain pertanyaan yang berkaitan dengan ekonomi, mohon untuk tidak menjawab.\n\n
                        Bold lah kata kunci yang penting dalam jawaban.\n\n
                    """
                ).text

        elif chat_request.chat_options == "2 Wheels":
            response = two_wheels_model(prompt)
            file_id_input = None  
            last_response = None
        
        elif chat_request.chat_options == "4 Wheels":
            response = four_wheels_model(prompt)
            file_id_input = None 
            last_response = None 
        
        elif chat_request.chat_options == "Retail General":
            response = retail_general_model(prompt)
            file_id_input = None  
            last_response = None

        elif chat_request.chat_options == "Retail Beauty":
            response = retail_beauty_model(prompt)
            file_id_input = None  
            last_response = None

        elif chat_request.chat_options == "Retail FnB":
            response = retail_fnb_model(prompt)
            file_id_input = None  
            last_response = None

        elif chat_request.chat_options == "Retail Drugstore":
            response = retail_drugstore_model(prompt)
            file_id_input = None  
            last_response = None

        chat_ref.update({
            'messages': firestore.ArrayUnion([
                {
                    'role': 'user',
                    'content': f"""
                        ## Ini adalah Last Response dari Percakapan Sebelumnya: {last_response}
                        \n\n
                        ## Pertanyaan Saat Ini: {prompt}
                        """,
                    'file_id': file_id_input,
                    'created_at': now
                },
                {
                    'role': 'assistant',
                    'content': response,
                    'created_at': now
                }
            ]),
            'last_response': response  
        })

        return {
            "response": response,
            "file_url": file_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))