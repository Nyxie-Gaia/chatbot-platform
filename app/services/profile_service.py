from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from ..models.database import User
from .graph_db import GraphService

class ProfileService:
    def __init__(self, db: Session, graph_service: GraphService):
        self.db = db
        self.graph_service = graph_service

    def create_user(self, username: str, email: str, hashed_password: str) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_profile(self, user_id: int) -> Dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        characteristics = self.graph_service.get_user_characteristics(str(user_id))
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "characteristics": characteristics,
            "created_at": user.created_at
        }

    def update_user_characteristics(self, user_id: int, characteristics: Dict[str, str]) -> None:
        for char, value in characteristics.items():
            self.graph_service.add_user_characteristic(str(user_id), char, value)

    def search_users(self, criteria: Dict[str, str], exclude_user_id: Optional[int] = None) -> List[Dict]:
        matching_usernames = self.graph_service.find_users_by_characteristics(criteria)
        
        users = []
        for username in matching_usernames:
            user = self.db.query(User).filter(User.username == username).first()
            if user and (not exclude_user_id or user.id != exclude_user_id):
                characteristics = self.graph_service.get_user_characteristics(str(user.id))
                users.append({
                    "id": user.id,
                    "username": user.username,
                    "characteristics": characteristics
                })
        
        return users

    def get_user_suggestions(self, user_id: int, limit: int = 5) -> List[Dict]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        similar_usernames = self.graph_service.find_similar_users(str(user_id), limit)
        
        suggestions = []
        for username in similar_usernames:
            other_user = self.db.query(User).filter(User.username == username).first()
            if other_user:
                characteristics = self.graph_service.get_user_characteristics(str(other_user.id))
                suggestions.append({
                    "id": other_user.id,
                    "username": other_user.username,
                    "characteristics": characteristics
                })
        
        return suggestions