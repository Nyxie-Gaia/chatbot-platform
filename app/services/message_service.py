from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..models.database import Message, User

class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, sender_id: int, recipient_id: int, content: str) -> Message:
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            timestamp=datetime.utcnow()
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_conversation(self, user1_id: int, user2_id: int, limit: int = 50) -> List[Message]:
        return self.db.query(Message).filter(
            ((Message.sender_id == user1_id) & (Message.recipient_id == user2_id)) |
            ((Message.sender_id == user2_id) & (Message.recipient_id == user1_id))
        ).order_by(Message.timestamp.desc()).limit(limit).all()

    def get_user_conversations(self, user_id: int) -> List[dict]:
        # Get all conversations where the user is either sender or recipient
        messages = self.db.query(Message).filter(
            (Message.sender_id == user_id) | (Message.recipient_id == user_id)
        ).order_by(Message.timestamp.desc()).all()

        # Group messages by conversation partner
        conversations = {}
        for message in messages:
            other_user_id = message.recipient_id if message.sender_id == user_id else message.sender_id
            
            if other_user_id not in conversations:
                other_user = self.db.query(User).filter(User.id == other_user_id).first()
                conversations[other_user_id] = {
                    "user": other_user,
                    "last_message": message,
                    "unread_count": 0
                }
            
            # Count unread messages
            if message.recipient_id == user_id and not message.read:
                conversations[other_user_id]["unread_count"] += 1

        return list(conversations.values())

    def mark_messages_as_read(self, recipient_id: int, sender_id: int) -> None:
        self.db.query(Message).filter(
            (Message.recipient_id == recipient_id) &
            (Message.sender_id == sender_id) &
            (Message.read == False)
        ).update({"read": True})
        self.db.commit()

    def delete_message(self, message_id: int, user_id: int) -> bool:
        message = self.db.query(Message).filter(
            Message.id == message_id,
            (Message.sender_id == user_id) | (Message.recipient_id == user_id)
        ).first()
        
        if message:
            self.db.delete(message)
            self.db.commit()
            return True
        return False