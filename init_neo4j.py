from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def init_neo4j():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    with driver.session() as session:
        # Create constraints
        session.run("CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE")
        session.run("CREATE CONSTRAINT characteristic_name_value IF NOT EXISTS FOR (c:Characteristic) REQUIRE (c.name, c.value) IS UNIQUE")
    
    driver.close()
    print("Neo4j database initialized successfully")