from abc import ABC, abstractmethod 
from typing import List, Optional, Union
from enum import Enum, auto

try:
    from knowledge_service import domain
except ModuleNotFoundError:
    import domain
except ImportError:
    import domain


class KnowledgeServiceError(Exception):
    """Base exception for Knowledge Service errors"""
    pass

class ResourceProcessingError(KnowledgeServiceError):
    """Error during resource processing"""
    pass

class EmbeddingError(KnowledgeServiceError):
    """Error generating embeddings"""
    pass
class ResourceProcessingError(Exception):
    """Base class for resource processing errors"""
    pass


class VirusDetectedError(ResourceProcessingError):
    """Raised when a virus is detected in a resource"""
    pass


class FileValidationError(ResourceProcessingError):
    """Raised when file validation fails"""
    pass


class FileAnalysisResult(Enum):
    CLEAN = auto()
    INFECTED = auto()
    ERROR = auto()

class FileManagerRepository(ABC):
    @abstractmethod
    def get_supported_file_types(self) -> List[str]:
        """Return list of supported MIME types

        Returns:
            List of supported MIME type strings
        """
        pass

    @abstractmethod
    def detect_file_type(self, resource: domain.Resource) -> Optional[str]:
        """Detect MIME type of file content

        Args:
            resource: Resource object containing the file to analyze

        Returns:
            Detected MIME type or None if unable to determine
        """
        pass

    @abstractmethod
    def scan_for_viruses(self, resource: domain.Resource) -> FileAnalysisResult:
        """Scan file for viruses/malware"""
        pass

    @abstractmethod
    def validate_file_format(self, resource: domain.Resource) -> bool:
        """Validate file format matches declared type"""
        pass

    @abstractmethod
    def extract_markdown_content(self, resource: domain.Resource) -> domain.Resource:
        """Extract markdown content from resource file

        Args:
            resource: Resource containing file to extract from

        Returns:
            Updated resource with markdown_content field set

        Raises:
            Exception: If extraction fails
        """
        pass

class VirusQuarantineRepository(ABC):
    @abstractmethod
    def quarantine_resource(self, resource: domain.Resource) -> bool:
        """Move infected resource to quarantine

        Args:
            resource: Resource object containing infected file

        Returns:
            True if quarantine successful, False otherwise
        """
        pass

    @abstractmethod
    def is_quarantined(self, resource_id: str) -> bool:
        """Check if a resource is quarantined

        Args:
            resource_id: ID of resource to check

        Returns:
            True if resource is in quarantine, False otherwise
        """
        pass

class TaskDispatchRepository(ABC):
    @abstractmethod
    def send_quarantine_notification(self, resource_id: str) -> None:
        """Send notification that resource was quarantined"""
        pass

    @abstractmethod
    def send_validation_error_notification(self, resource_id: str) -> None:
        """Send notification that resource validation failed"""
        pass

    @abstractmethod
    def extract_plain_text_of_resource(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def initiate_processing_of_new_resource(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def initiate_resource_graph(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def chunk_resource_text(self, resource_id: str) -> None:
        """Dispatch task to chunk resource text"""
        pass

    @abstractmethod
    def ventilate_resource_processing(self, resource_id: str) -> None:
        """Dispatch task to ventilate resource processing completion"""


class GraphRepository(ABC):
    @abstractmethod
    def check_resource_node_exists(self, resource_id: str) -> bool:
        pass

    @abstractmethod
    def upsert_resource_node(self, subscription: domain.Subscription, collection: domain.Collection, resource: domain.Resource) -> None:
        pass

    @abstractmethod
    def create_chunk_nodes(self, chunks: List[domain.ResourceChunk]) -> None:
        """Create nodes for resource chunks in the graph

        Args:
            chunks: List of chunks to create nodes for
        """
        pass

    @abstractmethod 
    def update_chunk_embedding(self, chunk: domain.ResourceChunk, embedding: List[float]) -> None:
        """Update a chunk's embedding vector

        Args:
            chunk: Chunk to update
            embedding: Embedding vector to store
        """
        pass

    @abstractmethod
    def get_chunks_without_embeddings(self, resource_id: str) -> List[domain.ResourceChunk]:
        """Get chunks that don't have embeddings yet

        Args:
            resource_id: ID of resource to get chunks for

        Returns:
            List of chunks without embeddings
        """
        pass


class CollectionRepository(ABC):
    @abstractmethod
    def get_collection_by_subscription_and_name(
        self, *args, **kwargs
    ) -> domain.Collection:
        pass

    @abstractmethod
    def create_new_collection(self, *args, **kwargs) -> domain.Collection:
        pass


class ResourceTypeRepository(ABC):
    @abstractmethod
    def get_resource_type_by_id(self, *args, **kwargs) -> domain.ResourceType:
        pass

    @abstractmethod
    def get_resource_type_list(
        self, *args, **kwargs
    ) -> List[domain.ResourceType]:
        pass


class ResourceRepository(ABC):
    @abstractmethod
    def get_resource_by_id(self, resource_id: str) -> Optional[domain.Resource]:
        """Get a resource by its ID

        Args:
            resource_id: Unique identifier of the resource

        Returns:
            The resource if found, None otherwise
        """
        pass

    @abstractmethod
    def get_resource_list(self, *args, **kwargs) -> List[domain.Resource]:
        """Get list of all resources"""
        pass

    @abstractmethod
    def get_resource_list_for_collection(
        self, *args, **kwargs
    ) -> Optional[domain.Resource]:
        pass

    @abstractmethod 
    def create_new_resource(
        self,
        collection_id: str,
        resource_type_id: str,
        name: str,
        file_name: str, 
        file: bytes,
        callback_urls: Optional[List[str]] = None
    ) -> domain.Resource:
        """Create a new resource with the given attributes"""
        pass

    @abstractmethod
    def update_resource(
            self,
            resource: domain.Resource
    ) -> domain.Resource:
        """Clobber/patch if different (else noop)"""
        pass

    @abstractmethod
    def set_file_type_for_resource_id(
        self, *args, **kwargs
    ) -> Optional[domain.Resource]:
        pass

    @abstractmethod
    def count_resources_in_collection(self, collection_id: str) -> int:
        """Count number of resources in a collection

        Args:
            collection_id: ID of the collection

        Returns:
            Number of resources in the collection
        """
        pass


class SubscriptionRepository(ABC):
    @abstractmethod
    def get_subscription_list(
        self, *args, **kwargs
    ) -> List[domain.Subscription]:
        pass

    @abstractmethod
    def get_subscription_details(self, *args, **kwargs) -> domain.Subscription:
        pass

    @abstractmethod
    def delete_subscription(self, *args, **kwargs) -> None:
        pass  # TODO: make bool return-type

    @abstractmethod
    def create_new_subscription(self, *args, **kwargs) -> domain.Subscription:
        pass




 #
 # stubs
 #
class DumbRepo(ABC):
    @abstractmethod
    def create(self, *args, **kwargs) -> domain.User:
        pass

    @abstractmethod
    def get_by_id(self, object_id: int) -> Optional[domain.User]:
        pass

    @abstractmethod
    def update(self, object_id: int, *args, **kwargs) -> domain.User:
        pass

    @abstractmethod
    def delete(self, object_id: int) -> None:
        pass
class LanguageModelRepository(ABC):
    @abstractmethod 
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text

        Args:
            text: Text to generate embedding for

        Returns:
            List of float values representing the embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass

    @abstractmethod
    def generate_rag_response(self, prompt: str, context: List[str]) -> str:
        """Generate RAG response from prompt and context

        Args:
            prompt: Query prompt
            context: List of relevant text chunks

        Returns:
            Generated response text

        Raises:
            Exception: If generation fails
        """
        pass
class ChunkingRepository(ABC):
    @abstractmethod
    def chunk_resource(
            self,
            resource_type: domain.ResourceType,
            resource: domain.Resource
    ) -> List[domain.ResourceChunk]:
        """Split resource content into chunks based on resource type strategy

        Args:
            resource_type: Type of resource determining chunking strategy
            resource: Resource to chunk

        Returns:
            List of chunks with text and metadata

        Raises:
            Exception: If chunking fails
        """
        pass
class SearchRepository(ABC):
    @abstractmethod
    def save_search_request(self, collection_id: str, query: str, filters: Optional[dict] = None) -> str:
        """Save a new search request

        Args:
            collection_id: ID of collection to search
            query: Search query text
            filters: Optional search filters

        Returns:
            ID of the created search request
        """
        pass

    @abstractmethod
    def get_search_request(self, search_id: str) -> Optional[domain.SearchRequest]:
        """Get a search request by ID

        Args:
            search_id: ID of search request

        Returns:
            SearchRequest if found, None otherwise
        """
        pass

    @abstractmethod
    def save_search_results(self, search_id: str, results: List[domain.SearchResult]) -> None:
        """Save search results for a request

        Args:
            search_id: ID of search request
            results: List of search results to save
        """
        pass
