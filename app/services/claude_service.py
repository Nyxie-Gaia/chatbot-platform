import anthropic
from typing import Dict, List, Tuple
import os

class ClaudeService:
    def __init__(self):
        self.client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.system_prompt = """You are a helpful AI assistant managing a chat platform. Your tasks include:
1. Extracting user characteristics from conversations
2. Helping users find other users based on characteristics
3. Facilitating communication between users
4. Maintaining conversation context

When extracting characteristics, focus on:
- Interests and hobbies
- Professional background
- Personal traits
- Skills and expertise"""

    async def process_message(self, user_id: str, message: str) -> Tuple[str, Dict[str, str]]:
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Process this message and extract any relevant user characteristics: {message}"
                }]
            )
            
            # Extract characteristics from Claude's analysis
            characteristics = self._extract_characteristics(response.content)
            
            return response.content, characteristics
        except Exception as e:
            print(f"Error processing message: {e}")
            return "I apologize, but I'm having trouble processing your message.", {}

    async def find_matching_users(self, query: str) -> Dict[str, str]:
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Convert this user search query into characteristics: {query}"
                }]
            )
            
            # Convert Claude's response into search criteria
            return self._extract_characteristics(response.content)
        except Exception as e:
            print(f"Error finding matching users: {e}")
            return {}

    def _extract_characteristics(self, claude_response: str) -> Dict[str, str]:
        characteristics = {}
        try:
            # Split the response into lines and look for key-value patterns
            lines = claude_response.split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if key and value:
                        characteristics[key] = value
        except Exception as e:
            print(f"Error extracting characteristics: {e}")
        
        return characteristics