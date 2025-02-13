import os

from neo4j import GraphDatabase

try:
    from knowledge_service import domain, repositories
except ModuleNotFoundError:
    import domain
    import repositories
except ImportError:
    import domain
    import repositories

# Initialize the Neo4j driver
uri = os.getenv("X_NEO4J_URI", "neo4j://neo4j:7687")
neo4j_auth_string = os.getenv("NEO4J_AUTH", "neo4j/neo4j_psx")
username = neo4j_auth_string.split("/")[0]
password = neo4j_auth_string.split("/")[1]


class Neo4jGraphRepository(repositories.GraphRepository):
    def check_resource_node_exists(self, resource_id: str) -> bool:
        query = """
        MATCH (r:Resource)
        WHERE r.resource_id = $resource_id
        RETURN r
        LIMIT 1
        """
        driver = GraphDatabase.driver(uri, auth=(username, password))
        with driver.session() as session:
            result = session.run(query, resource_id=resource_id)
            return result.single() is not None

    def upsert_resource_node(
        self,
        subscription: domain.Subscription,
        collection: domain.Collection,
        resource: domain.Resource,
    ) -> None:
        query = """
        MERGE (s:Subscription {subscription_id: $subscription_id})
        SET s.name = $subscription_name
        MERGE (c:Collection {collection_id: $collection_id})
        SET c.name = $collection_name
        MERGE (s)-[:OWNS]->(c)
        MERGE (r:Resource {resource_id: $resource_id})
        SET r.file_name = $file_name
        SET r.file_type = $file_type
        MERGE (c)-[:CONTAINS]-(r)
        RETURN s, c, r
        """
        driver = GraphDatabase.driver(uri, auth=(username, password))
        with driver.session() as session:
            result = session.run(
                query,
                subscription_id=subscription.id,
                subscription_name=subscription.name,
                collection_id=collection.id,
                collection_name=collection.name,
                resource_id=resource.id,
                file_name=resource.file_name,
                file_type=resource.file_type,
            )
            return result.single() is not None
from typing import List, Optional
from knowledge_service import domain
from knowledge_service.repositories import GraphRepository

class Neo4jGraphRepository(GraphRepository):
    def check_resource_node_exists(self, resource_id: str) -> bool:
        # TODO: Implement actual Neo4j query
        return False

    def upsert_resource_node(self, subscription: domain.Subscription, collection: domain.Collection, resource: domain.Resource) -> None:
        # TODO: Implement actual Neo4j query
        pass

    def create_chunk_nodes(self, chunks: List[domain.ResourceChunk]) -> None:
        """Create nodes for resource chunks in the graph

        Args:
            chunks: List of chunks to create nodes for
        """
        # TODO: Implement actual Neo4j query to create chunk nodes
        pass

    def update_chunk_embedding(self, chunk: domain.ResourceChunk, embedding: List[float]) -> None:
        """Update a chunk's embedding vector

        Args:
            chunk: Chunk to update
            embedding: Embedding vector to store
        """
        # TODO: Implement actual Neo4j query to update embedding
        pass

    def get_chunks_without_embeddings(self, resource_id: str) -> List[domain.ResourceChunk]:
        """Get chunks that don't have embeddings yet

        Args:
            resource_id: ID of resource to get chunks for

        Returns:
            List of chunks without embeddings
        """
        # TODO: Implement actual Neo4j query
        return []
