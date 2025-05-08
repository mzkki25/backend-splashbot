from fastapi import APIRouter, Depends, HTTPException
from models.schemas import ChatHistory, ChatMessage
from core.firebase import db
from api.deps import get_current_user
from typing import List

router = APIRouter()

@router.get("", response_model=List[ChatMessage])
async def get_chat_messages(chat_session: str, user=Depends(get_current_user)):
    try:
        user_id = user['uid']

        chat_ref = db.collection('chats').document(chat_session)
        chat_doc = chat_ref.get()

        if not chat_doc.exists:
            raise HTTPException(status_code=404, detail="Chat not found")

        chat_data = chat_doc.to_dict()

        if chat_data['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to chat")

        messages = chat_data.get('messages', [])

        messages_sorted = sorted(
            messages, key=lambda x: x.get('created_at', 0) 
        )

        results = []
        for msg in messages_sorted:
            created_at = msg.get('created_at')
            if created_at:
                if isinstance(created_at, (int, float)):
                    timestamp_str = str(int(created_at))
                else:
                    timestamp_str = created_at.isoformat()
            else:
                timestamp_str = None

            results.append(
                ChatMessage(
                    message_id=msg.get('message_id', ''),
                    chat_session_id=chat_session,
                    role=msg.get('role', ''),
                    content=msg.get('content', ''),
                    file_id=msg.get('file_id'),
                    timestamp=timestamp_str,
                    references=msg.get('references', [])
                ))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))