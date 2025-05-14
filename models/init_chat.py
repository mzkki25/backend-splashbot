from fastapi import HTTPException

from core.firebase import db, bucket
from core.gemini import model, multimodal_model
from utils.semantic_search import find_relevant_chunks, extract_pdf_text_and_tables_from_blob
from utils.makroeconomics import (
    two_wheels_model, four_wheels_model, retail_general_model,
    retail_beauty_model, retail_fnb_model, retail_drugstore_model
)
from utils.search_web import search_web_snippets
from utils.follow_up_question import (
    recommend_follow_up_questions_gm,
    recommend_follow_up_questions_ngm
)
from PIL import Image
from firebase_admin import firestore
from datetime import datetime

import io
import uuid

class Chat:
    def __init__(self):
        self.now = datetime.now()

    def init_or_update_chat(self, chat_session, user_id, prompt, file_id_input):
        chat_ref = db.collection('chats').document(chat_session)
        chat_doc = chat_ref.get()
        last_response = None

        if not chat_doc.exists:
            chat_title = prompt[:17] + "..." if len(prompt) > 17 else prompt
            chat_ref.set({
                'user_id': user_id,
                'title': chat_title,
                'status': 'active',
                'messages': [],
                'created_at': firestore.SERVER_TIMESTAMP,
                'last_file_id': file_id_input,
                'last_response': None
            })
        else:
            chat_data = chat_doc.to_dict()
            last_response = chat_data.get("last_response")
            last_file_id = chat_data.get("last_file_id")

            if file_id_input and file_id_input != last_file_id:
                chat_ref.update({'last_file_id': file_id_input})
            elif not file_id_input and last_file_id:
                file_id_input = last_file_id

        return chat_ref, last_response, file_id_input

    async def generate_response(self, chat_option, prompt, file_id_input, last_response):
        file_url = None
        references = None

        if chat_option == "General Macroeconomics":
            if file_id_input:
                file_url, response = self._handle_file_prompt(prompt, file_id_input, last_response)
                follow_up_question = recommend_follow_up_questions_gm(prompt, response, file_id_input)
            else:
                response, references = self._handle_web_prompt(prompt, last_response)
                follow_up_question = recommend_follow_up_questions_gm(prompt, response)
        else:
            response = self._handle_custom_model(chat_option, prompt)
            follow_up_question = recommend_follow_up_questions_ngm(prompt, response, chat_option)
            file_id_input = None

        return response, file_url, references, follow_up_question

    def _handle_file_prompt(self, prompt, file_id_input, last_response):
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
            relevant_text = find_relevant_chunks(pdf_text, prompt, chunk_size=650, top_k=5) if len(pdf_text) > 1000 else pdf_text

            response = model.generate_content(
                f"""
                Kamu adalah **SPLASHBot**, AI Agent yang mengkhususkan diri dalam **analisis dokumen ekonomi**, khususnya file **PDF** yang diberikan oleh pengguna.

                ### Informasi yang Disediakan:
                - **Konten relevan dari PDF**:  
                {relevant_text}

                - **Pertanyaan dari pengguna**:  
                "{prompt}"

                - **Respons terakhir dari percakapan sebelumnya**:  
                {last_response}

                ### Aturan Penting:
                1. **Hanya jawab pertanyaan** jika isi PDF berkaitan dengan **ekonomi**.  
                Jika tidak relevan secara ekonomi, jawab dengan:  
                _"Maaf, saya hanya dapat menjawab pertanyaan yang berkaitan dengan ekonomi."_
                2. Soroti **kata kunci penting** dalam jawaban dengan **bold** agar mudah dikenali.
                3. Jawaban harus **jelas**, **fokus pada konteks ekonomi**, dan **berdasarkan isi PDF**.

                ### Tugas:
                Berikan jawaban berbasis analisis isi PDF tersebut, dengan tetap menjaga fokus pada aspek ekonomi dan pertanyaan pengguna.
                """
            ).text

        elif content_type.startswith('image/'):
            image = Image.open(io.BytesIO(file_content)).convert("RGB")
            response = multimodal_model.generate_content(
                [
                    "Kamu adalah SPLASHBot yang mengkhususkan diri dalam ekonomi dan menganalisis gambar yang diberikan.",
                    image,
                    f"""
                    Pertanyaan dari user: {prompt}
                    Ini adalah last response dari percakapan sebelumnya: {last_response}

                    Apabila gambar yang diberikan bukan berkaitan dengan ekonomi, mohon untuk tidak menjawab.
                    Bold lah kata kunci yang penting dalam jawaban.
                    """
                ]
            ).text

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        return file_url, response

    def _handle_web_prompt(self, prompt, last_response):
        result = search_web_snippets(prompt, num_results=5)
        references = result.get("linked_results", [])
        snippets = result.get("snippet_results", "")

        response = model.generate_content(
            f"""
            Kamu adalah **SPLASHBot**, sebuah AI Agent yang ahli dalam menjawab pertanyaan seputar **ekonomi**, termasuk ekonomi makro, mikro, kebijakan fiskal/moneter, perdagangan, keuangan, dan indikator ekonomi.

            ### Konteks Sebelumnya:
            {last_response}

            ### Pertanyaan dari Pengguna:
            {prompt}

            ### Informasi Terkini dari Internet:
            {snippets}

            ### Referensi:
            {references}

            ### Catatan Penting:
            - Gunakan **informasi dari internet** dan semua pengetahuan-mu jika **relevan dengan topik ekonomi**.
            - **Abaikan** informasi yang tidak berkaitan dengan ekonomi.
            - **Jangan menyebutkan atau mengutip link** dari internet secara eksplisit dalam jawaban.
            - Gunakan penekanan (**bold**) pada **kata kunci penting** dalam jawaban agar lebih jelas bagi pengguna.
            - Sebisa mungkin, jangan menjawab dengan "saya tidak tahu" atau "saya tidak bisa menjawab". Gunakan pengetahuan yang ada untuk memberikan jawaban yang informatif.

            ### Tugasmu:
            Berikan jawaban yang **jelas**, **relevan**, dan **berbasis ekonomi** terhadap pertanyaan pengguna. 
            Jika pertanyaannya **tidak berkaitan dengan ekonomi**, cukup balas dengan: _"Maaf, saya hanya dapat menjawab pertanyaan yang berkaitan dengan ekonomi."_
            """
        ).text

        return response, references

    def _handle_custom_model(self, chat_option, prompt):
        model_map = {
            "2 Wheels": two_wheels_model,
            "4 Wheels": four_wheels_model,
            "Retail General": retail_general_model,
            "Retail Beauty": retail_beauty_model,
            "Retail FnB": retail_fnb_model,
            "Retail Drugstore": retail_drugstore_model
        }

        model_func = model_map.get(chat_option)
        if not model_func:
            raise HTTPException(status_code=400, detail="Invalid chat option")
        
        return model_func(prompt)

    def save_chat_messages(self, chat_ref, chat_session, prompt, response, file_id_input, references):
        chat_ref.update({
            'messages': firestore.ArrayUnion([
                {
                    'message_id': f"user-{uuid.uuid4()}",
                    'chat_session_id': chat_session,
                    'role': 'user',
                    'content': prompt,
                    'file_id': file_id_input,
                    'created_at': self.now
                },
                {
                    'message_id': f"assistant-{uuid.uuid4()}",
                    'chat_session_id': chat_session,
                    'role': 'assistant',
                    'content': response,
                    'created_at': self.now,
                    'references': references,
                }
            ]),
            'last_response': response
        })