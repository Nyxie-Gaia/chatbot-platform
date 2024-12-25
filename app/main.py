from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

from .models.database import init_db, engine, SessionLocal, User
from .services.graph_db import GraphService
from .services.claude_service import ClaudeService
from .services.auth import (
    get_current_user,
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from .services.message_service import MessageService
from .services.profile_service import ProfileService

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
graph_service = GraphService()
claude_service = ClaudeService()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Service dependencies
def get_message_service(db: Session = Depends(get_db)) -> MessageService:
    return MessageService(db)

def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(db, graph_service)

# Initialize database
init_db()

# Routes
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register(
    username: str,
    email: str,
    password: str,
    profile_service: ProfileService = Depends(get_profile_service)
):
    hashed_password = get_password_hash(password)
    try:
        user = profile_service.create_user(username, email, hashed_password)
        return {"id": user.id, "username": user.username}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

@app.post("/api/chat")
async def chat(
    message: str,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    # Process message with Claude
    response, characteristics = await claude_service.process_message(str(current_user.id), message)
    
    # Store extracted characteristics
    if characteristics:
        profile_service.update_user_characteristics(current_user.id, characteristics)
    
    return {"response": response}

@app.post("/api/search-users")
async def search_users(
    query: str,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    # Convert search query to characteristics using Claude
    search_criteria = await claude_service.find_matching_users(query)
    
    # Find matching users
    matching_users = profile_service.search_users(search_criteria, exclude_user_id=current_user.id)
    
    return {"users": matching_users}

@app.post("/api/send-message")
async def send_message(
    recipient_id: int,
    content: str,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    message = message_service.create_message(current_user.id, recipient_id, content)
    return {
        "id": message.id,
        "content": message.content,
        "timestamp": message.timestamp
    }

@app.get("/api/messages/{other_user_id}")
async def get_messages(
    other_user_id: int,
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    messages = message_service.get_conversation(current_user.id, other_user_id)
    message_service.mark_messages_as_read(current_user.id, other_user_id)
    return {"messages": messages}

@app.get("/api/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(get_message_service)
):
    return {"conversations": message_service.get_user_conversations(current_user.id)}

@app.get("/api/profile")
async def get_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return profile_service.get_user_profile(current_user.id)

@app.get("/api/suggestions")
async def get_suggestions(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    return {"suggestions": profile_service.get_user_suggestions(current_user.id)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)