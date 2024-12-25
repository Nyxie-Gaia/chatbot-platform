from neo4j import GraphDatabase
from typing import List, Dict
import os

class GraphService:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def add_user_characteristic(self, username: str, characteristic: str, value: str):
        with self.driver.session() as session:
            session.execute_write(self._create_user_characteristic,
                                username, characteristic, value)

    @staticmethod
    def _create_user_characteristic(tx, username: str, characteristic: str, value: str):
        query = (
            "MERGE (u:User {username: $username}) "
            "MERGE (c:Characteristic {name: $characteristic, value: $value}) "
            "MERGE (u)-[:HAS]->(c)"
        )
        tx.run(query, username=username, characteristic=characteristic, value=value)

    def find_users_by_characteristics(self, characteristics: Dict[str, str]) -> List[str]:
        with self.driver.session() as session:
            return session.execute_read(self._find_users, characteristics)

    @staticmethod
    def _find_users(tx, characteristics: Dict[str, str]) -> List[str]:
        conditions = []
        params = {}
        for i, (char, value) in enumerate(characteristics.items()):
            conditions.append(f"(u)-[:HAS]->(:Characteristic {{name: $char{i}, value: $val{i}}})")
            params[f"char{i}"] = char
            params[f"val{i}"] = value

        query = (
            f"MATCH (u:User) "
            f"WHERE {' AND '.join(conditions)} "
            f"RETURN u.username as username"
        )
        result = tx.run(query, **params)
        return [record["username"] for record in result]

    def get_user_characteristics(self, username: str) -> Dict[str, str]:
        with self.driver.session() as session:
            return session.execute_read(self._get_characteristics, username)

    @staticmethod
    def _get_characteristics(tx, username: str) -> Dict[str, str]:
        query = (
            "MATCH (u:User {username: $username})-[:HAS]->(c:Characteristic) "
            "RETURN c.name as name, c.value as value"
        )
        result = tx.run(query, username=username)
        return {record["name"]: record["value"] for record in result}

    def find_similar_users(self, username: str, limit: int = 5) -> List[str]:
        with self.driver.session() as session:
            return session.execute_read(self._find_similar_users, username, limit)

    @staticmethod
    def _find_similar_users(tx, username: str, limit: int) -> List[str]:
        query = (
            "MATCH (u1:User {username: $username})-[:HAS]->(c:Characteristic)<-[:HAS]-(u2:User) "
            "WHERE u1 <> u2 "
            "WITH u2, count(c) as commonCharacteristics "
            "RETURN u2.username as username "
            "ORDER BY commonCharacteristics DESC "
            "LIMIT $limit"
        )
        result = tx.run(query, username=username, limit=limit)
        return [record["username"] for record in result]