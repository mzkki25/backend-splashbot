from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from utils.init_chat import init_or_update_chat, save_chat_messages, generate_response

from models.schemas import ChatRequest, ChatResponse

from api.deps import get_current_user
from datetime import datetime


now = datetime.now()
router = APIRouter()

@router.post("/{chat_session}", response_model=ChatResponse)
async def process_chat(chat_session: str, chat_request: ChatRequest, user = Depends(get_current_user)):
    try:
        user_id = user['uid']
        prompt = chat_request.prompt
        file_id_input = chat_request.file_id

        chat_ref, last_response, file_id_input = init_or_update_chat(chat_session, user_id, prompt, file_id_input)

        response, file_url, references = await generate_response(
            chat_request.chat_options, prompt, file_id_input, last_response
        )

        save_chat_messages(chat_ref, chat_session, prompt, response, file_id_input, references)

        return JSONResponse(content={
            "response": response,
            "file_url": file_url,
            "created_at": now.isoformat(),
            "references": references,
        }, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
