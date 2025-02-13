from typing import Dict, List, Optional
from uuid import UUID
import datetime

from knowledge_service import domain
from knowledge_service.repositories import (
    FileAnalysisResult,
    ChunkingRepository, 
    CollectionRepository,
    FileManagerRepository,
    GraphRepository,
    LanguageModelRepository,
    ResourceRepository,
    ResourceTypeRepository,
    SearchRepository,
    SubscriptionRepository,
    TaskDispatchRepository,
    VirusQuarantineRepository
)

class MockFileManagerRepository(FileManagerRepository):
    def __init__(self):
        self.supported_types = ["text/plain", "application/pdf"]

    def get_supported_file_types(self) -> List[str]:
        return self.supported_types

    def detect_file_type(self, resource: domain.Resource) -> Optional[str]:
        if resource.file.startswith(b"%PDF"):
            return "application/pdf"
        return "text/plain"

    def scan_for_viruses(self, resource: domain.Resource) -> FileAnalysisResult:
        if resource.file and b"VIRUS" in resource.file:
            return FileAnalysisResult.INFECTED 
        return FileAnalysisResult.CLEAN

    def validate_file_format(self, resource: domain.Resource) -> bool:
        return True

    def extract_markdown_content(self, resource: domain.Resource) -> domain.Resource:
        """Simple mock implementation that just copies file content to markdown"""
        resource.markdown_content = resource.file.decode('utf-8')
        return resource
class MockVirusQuarantineRepository(VirusQuarantineRepository):
    def __init__(self):
        self.quarantined = set()

    def quarantine_resource(self, resource: domain.Resource) -> bool:
        self.quarantined.add(resource.id)
        return True

    def is_quarantined(self, resource_id: str) -> bool:
        return resource_id in self.quarantined

class MockTaskDispatchRepository(TaskDispatchRepository):
    def __init__(self):
        self.notifications = []

    def send_quarantine_notification(self, resource_id: str) -> None:
        self.notifications.append(("quarantine", resource_id))

    def send_validation_error_notification(self, resource_id: str) -> None:
        self.notifications.append(("validation_error", resource_id))

    def update_chunks_with_embeddings(self, resource_id: str) -> None:
        self.notifications.append(("update_embeddings", resource_id))

    def extract_plain_text_of_resource(self, resource_id: str) -> None:
        self.notifications.append(("extract_text", resource_id))

    def initiate_processing_of_new_resource(self, *args, **kwargs) -> None:
        pass

    def initiate_resource_graph(self, *args, **kwargs) -> None:
        pass

    def chunk_resource_text(self, resource_id: str) -> None:
        self.notifications.append(("chunk_text", resource_id))

    def ventilate_resource_processing(self, resource_id: str) -> None:
        self.notifications.append(("ventilate_processing", resource_id))
class MockGraphRepository(GraphRepository):
    def __init__(self):
        self.nodes = {}

    def check_resource_node_exists(self, resource_id: str) -> bool:
        return resource_id in self.nodes

    def check_resource_node_exists(self, resource_id: str) -> bool:
        return resource_id in self.nodes

    def calculate_chunk_similarities(self, chunks: List[domain.ResourceChunk], query_embedding: List[float]) -> List[float]:
        """Mock implementation of similarity calculation"""
        # Return a similarity score for each chunk
        scores = []
        for chunk in chunks:
            if chunk.id == "chunk-1":
                scores.append(0.9)
            else:
                scores.append(0.8)
        return scores

    def get_relevant_chunks(self, search_id: str) -> Optional[List[domain.ResourceChunk]]:
        """Mock implementation of get_relevant_chunks"""
        chunks = []
        # Get all chunks and add mock scores
        for chunk in self.nodes.values():
            if isinstance(chunk, domain.ResourceChunk):
                chunk.score = 0.9 if chunk.id == "chunk-1" else 0.8
                chunk.similarity = chunk.score
                chunks.append(chunk)
        chunks.sort(key=lambda x: x.score, reverse=True)
        return chunks

    def upsert_resource_node(self, subscription: domain.Subscription, collection: domain.Collection, resource: domain.Resource) -> None:
        self.nodes[resource.id] = resource 

    def create_chunk_nodes(self, chunks: List[domain.ResourceChunk]) -> None:
        for chunk in chunks:
            self.nodes[chunk.id] = chunk

    def update_chunk_embedding(self, chunk: domain.ResourceChunk, embedding: List[float]) -> None:
        """Update a chunk's embedding vector"""
        if chunk.id in self.nodes:
            self.nodes[chunk.id].embedding = embedding

    def get_chunks_without_embeddings(self, resource_id: str) -> List[domain.ResourceChunk]:
        """Get chunks that don't have embeddings yet"""
        chunks = []
        for chunk in self.nodes.values():
            if isinstance(chunk, domain.ResourceChunk) and chunk.resource_id == resource_id:
                if not hasattr(chunk, 'embedding'):
                    chunks.append(chunk)
        return chunks
class MockCollectionRepository(CollectionRepository):
    def __init__(self):
        self.collections = {}

    def get_collection_by_id(self, collection_id: str) -> Optional[domain.Collection]:
        """Get collection by ID"""
        return self.collections.get(collection_id)

    def get_collection_by_subscription_and_name(self, subscription_id: UUID, name: str) -> Optional[domain.Collection]:
        for collection in self.collections.values():
            if collection.subscription_id == subscription_id and collection.name == name:
                return collection
        return None

    def create_new_collection(self, name: str, subscription_id: UUID, resource_type_ids: List[str], description: str = "") -> domain.Collection:
        collection = domain.Collection(
            id=str(UUID(int=len(self.collections))), 
            name=name,
            subscription_id=subscription_id,
            resource_types=[
                domain.ResourceType(
                    id=rt_id, name=f"Type {rt_id}", tooltip=f"Tooltip for {rt_id}"
                )
                for rt_id in resource_type_ids
            ],
            description=description
        )
        self.collections[collection.id] = collection
        return collection

    def delete_collection(self, collection_id: str) -> bool:
        if collection_id in self.collections:
            del self.collections[collection_id]
            return True
        return False
class MockResourceTypeRepository(ResourceTypeRepository):
    def __init__(self):
        self.resource_types = {}

    def get_resource_type_by_id(self, type_id: str) -> Optional[domain.ResourceType]:
        return self.resource_types.get(type_id)

    def get_resource_type_list(self) -> List[domain.ResourceType]:
        return list(self.resource_types.values())

class MockResourceRepository(ResourceRepository):
    def __init__(self):
        self.resources = {}

    def get_resource_by_id(self, resource_id: str) -> Optional[domain.Resource]:
        return self.resources.get(resource_id)

    def get_resource_list(self) -> List[domain.Resource]:
        return list(self.resources.values())

    def get_resource_list_for_collection(self, collection_id: str) -> List[domain.Resource]:
        return [r for r in self.resources.values() if r.collection_id == collection_id]

    def create_new_resource(self, collection_id: str, resource_type_id: str, 
                          name: str, file_name: str, file: bytes,
                          callback_urls: Optional[List[str]] = None) -> domain.Resource:
        resource = domain.Resource( 
            id=f"test-resource-{len(self.resources)}",  # Simple predictable ID
            collection_id=collection_id,
            resource_type_id=resource_type_id,
            name=name,
            file_name=file_name,
            file=file,
            file_type=None,  # Will be detected later
            metadata_file={},  # Empty metadata initially
            callback_urls=callback_urls or []
        )
        # Store with string ID to ensure consistent lookup
        self.resources[str(resource.id)] = resource
        return resource

    def update_resource(self, resource: domain.Resource) -> domain.Resource:
        self.resources[resource.id] = resource
        return resource

    def delete_resource(self, resource_id: str) -> None:
        if resource_id in self.resources:
            del self.resources[resource_id]

    def set_file_type_for_resource_id(self, resource_id: str, file_type: str) -> Optional[domain.Resource]:
        if resource := self.resources.get(resource_id):
            resource.file_type = file_type
            return resource
        return None

    def count_resources_in_collection(self, collection_id: str) -> int:
        """Count resources in collection using list comprehension"""
        return len([r for r in self.resources.values() if r.collection_id == collection_id])

class MockSubscriptionRepository(SubscriptionRepository):
    def __init__(self):
        self.subscriptions = {}

    def get_subscription_list(self) -> List[domain.Subscription]:
        return list(self.subscriptions.values())

    def get_subscription_details(self, subscription_id: UUID) -> Optional[domain.Subscription]:
        return self.subscriptions.get(subscription_id)

    def delete_subscription(self, subscription_id: UUID) -> bool:
        if subscription_id in self.subscriptions:
            del self.subscriptions[subscription_id]
            return True
        return False


    def create_new_subscription(self, name: str, resource_type_ids: List[str], status: str) -> domain.Subscription:
        subscription = domain.Subscription(
            id=str(UUID(int=len(self.subscriptions))),
            name=name,
            is_active=(status == "active"),
            resource_types=[
                domain.ResourceType(id=rt_id, name=f"Type {rt_id}", tooltip=f"Tooltip for {rt_id}")
                for rt_id in resource_type_ids
            ],
            collections=[]
        )
        self.subscriptions[subscription.id] = subscription
        return subscription

class MockLanguageModelRepository(LanguageModelRepository):
    def __init__(self):
        self.embeddings = {}

    def generate_embedding(self, text: str) -> List[float]:
        # Simple mock embedding - just hash the text to a few floats
        h = hash(text)
        return [float(h % 100), float((h//100) % 100), float((h//10000) % 100)]

    def generate_rag_response(self, prompt: str, context: List[str]) -> str:
        return f"Mock RAG response for prompt: {prompt} with {len(context)} context chunks"

    def generate_credential(self) -> None:
        """Mock implementation of credential generation"""
        return None

class MockChunkingRepository(ChunkingRepository):
    def chunk_resource(
            self,
            resource_type: domain.ResourceType,
            resource: domain.Resource
    ) -> List[domain.ResourceChunk]:
        # Simple chunking - split on newlines
        if not resource.markdown_content:
            return []

        chunks = []
        for i, text in enumerate(resource.markdown_content.split("\n\n")): 
            if text.strip():
                chunks.append(domain.ResourceChunk(
                    id=f"{resource.id}_chunk_{i}",
                    resource_id=resource.id,
                    text=text,
                    sequence=i,
                    extract=text,  # Using the same text as extract for simplicity
                    metadata={"position": i}
                ))
        return chunks

class MockSearchRepository(SearchRepository):
    def __init__(self):
        self.search_requests = {}
        self.search_results = {}

    def save_search_request(self, collection_id: str, query: str, filters: Optional[dict] = None, callback_urls: Optional[List[str]] = None) -> str:
        search_id = str(UUID(int=len(self.search_requests)))
        self.search_requests[search_id] = domain.SearchRequest(
            id=search_id,
            collection_id=collection_id,
            query=query,
            filters=filters or {},
            created_at=datetime.datetime.now(),
            callback_urls=callback_urls
        )
        return search_id

    def get_search_request(self, search_id: str) -> Optional[domain.SearchRequest]:
        return self.search_requests.get(search_id)

    def save_search_results(self, search_id: str, results: List[domain.SearchResult]) -> None:
        self.search_results[search_id] = results
