from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from models.schemas import UserCreate, UserLogin
from core.firebase import db, auth
from firebase_admin import firestore

router = APIRouter()

@router.post("/signup")
async def signup(user: UserCreate):
    try:
        user_record = auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.username
        )

        db.collection('users').document(user_record.uid).set({
            'email': user.email,
            'username': user.username,
            'password': user.password,
            'created_at': firestore.SERVER_TIMESTAMP,
        })

        return JSONResponse(
            content={
                "success": True,
                "user_id": user_record.uid
            },
            status_code=status.HTTP_201_CREATED
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login")
async def login(user: UserLogin):
    try:
        if '@' in user.email_or_username:
            users = db.collection('users').where('email', '==', user.email_or_username).limit(1).get()
        else:
            users = db.collection('users').where('username', '==', user.email_or_username).limit(1).get()

        if not users:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        user_data = users[0].to_dict()
        email = user_data.get('email')
        saved_password = user_data.get('password')

        if user.password != saved_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        user_record = auth.get_user_by_email(email)
        custom_token = auth.create_custom_token(user_record.uid)

        return JSONResponse(
            content={
                "success": True,
                "user_id": user_record.uid,
                "token": custom_token.decode('utf-8')
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))