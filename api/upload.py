from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from core.firebase import db, bucket
from api.deps import get_current_user
from firebase_admin import firestore

import uuid
import os

router = APIRouter()

@router.post("")
async def upload_file(file: UploadFile = File(...), user = Depends(get_current_user)):
    try:
        user_id = user['uid']
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        file_path = f"users/{user_id}/{file_id}{file_extension}"

        blob = bucket.blob(file_path)
        contents = await file.read()
        blob.upload_from_string(contents, content_type=file.content_type)

        db.collection('files').document(file_id).set({
            'user_id': user_id,
            'filename': file.filename,
            'content_type': file.content_type,
            'storage_path': file_path,
            'url': blob.public_url,
            'created_at': firestore.SERVER_TIMESTAMP
        })

        return JSONResponse({
            "success": True,
            "file_id": file_id,
            "url": blob.public_url
        }, status_code=201)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
