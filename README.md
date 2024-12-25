# AI-Driven Chat Platform

A sophisticated chat platform that uses AI to help users connect based on shared interests and characteristics.

## Features

- AI-powered user matching using Claude
- Real-time chat functionality
- Automatic characteristic extraction from conversations
- User discovery through natural language search
- Persistent conversation history
- Profile management with extracted characteristics
- Secure authentication system

## Technology Stack

- Backend: FastAPI
- Database: SQLite (user data) + Neo4j (user characteristics)
- AI: Claude API (Anthropic)
- Frontend: HTML + Tailwind CSS + JavaScript

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
ANTHROPIC_API_KEY=your_anthropic_api_key
SECRET_KEY=your_secret_key
```

3. Initialize databases:
```bash
python run.py
```

## Architecture

The platform consists of several key components:

1. User Management
   - Authentication using JWT tokens
   - Profile management with characteristic tracking

2. Chat System
   - Direct messaging between users
   - AI-assisted conversations with Claude
   - Message history and read status tracking

3. User Discovery
   - Natural language search using Claude
   - Graph-based user matching
   - Automatic suggestion system

4. Data Storage
   - SQLite for user accounts and messages
   - Neo4j for characteristic-based matching
   - Graph relationships for efficient user discovery

## API Endpoints

- `/api/chat` - Chat with Claude
- `/api/search-users` - Search for users
- `/api/send-message` - Send messages to users
- `/api/messages/{user_id}` - Get conversation history
- `/api/conversations` - List active conversations
- `/api/profile` - View and update profile
- `/api/suggestions` - Get user suggestions

## Security

- Password hashing using bcrypt
- JWT token authentication
- Input validation and sanitization
- Secure session management
- Protected API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request