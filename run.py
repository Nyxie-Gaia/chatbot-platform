import uvicorn
from app.models.database import init_db
from init_neo4j import init_neo4j

if __name__ == "__main__":
    # Initialize databases
    print("Initializing SQLite database...")
    init_db()
    
    print("Initializing Neo4j database...")
    init_neo4j()
    
    # Run the application
    print("Starting the application...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)