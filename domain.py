"""
The logical entities in the Knowledge Service system.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class ResourceType:
    """Represents a type of resource that can be stored in collections.

    Attributes:
        id: Unique identifier for the resource type
        name: Display name of the resource type
        tooltip: Help text describing the resource type
    """

    id: str
    name: str
    tooltip: str


@dataclass
class Collection:
    """A collection of resources belonging to a subscription.

    Attributes:
        id: Unique identifier for the collection
        subscription_id: ID of the subscription this collection belongs to
        resource_type_ids: List of resource type IDs allowed in this collection
        name: Display name of the collection
        description: Optional description of the collection's purpose
    """

    id: str
    subscription_id: str
    resource_types: List[ResourceType]
    name: str = ""
    description: Optional[str] = None


@dataclass 
class Resource:
    """An individual resource stored in a collection.

    Attributes:
        id: Unique identifier for the resource
        collection_id: ID of the collection this resource belongs to
        resource_type_id: Type of resource
        name: Display name of the resource
        file_name: Name of the stored file
        file_type: MIME type of the file
        file: The actual file contents
        metadata_file: Additional metadata about the resource
        callback_urls: URLs to notify when resource is updated
    """

    id: str
    collection_id: str
    resource_type_id: Optional[str]
    name: Optional[str]
    file_name: str
    file_type: Optional[str]
    file: Optional[bytes]
    metadata_file: Optional[bytes]
    callback_urls: Optional[List[str]] = None
    markdown_content: Optional[str] = None
    status: str = "pending"


@dataclass
class Subscription:
    """A subscription that can contain multiple collections.

    Attributes:
        id: Unique identifier for the subscription
        name: Display name of the subscription
        is_active: Whether the subscription is currently active
        resource_types: List of allowed resource types
        collections: List of collections in this subscription
        organisation_id: Optional ID of the owning organization
        user_id: Optional ID of the owning user
        Note: Either organisation_id or user_id must be set, but not both
    """

    id: str
    name: str
    is_active: bool
    resource_types: List[ResourceType]
    collections: List[Collection]
    organisation_id: Optional[int] = None
    user_id: Optional[int] = None


@dataclass
class User:
    """A user account in the system.

    Attributes:
        id: Unique identifier for the user
        username: User's login name
        email: User's email address
        password: Hashed password
    """

    id: int
    username: str
    email: str
    password: str


@dataclass
class Organisation:
    """An organization that can contain multiple users.

    Attributes:
        id: Unique identifier for the organization
        name: Organization name
        description: Optional description of the organization
        users: List of user IDs belonging to this organization
    """

    id: int
    name: str
    description: Optional[str] = None
    users: List[int] = None  # List of user ids


@dataclass
class SearchRequest:
    """A request to search resources or collections

    Attributes:
        id: Unique identifier for the search request
        query: The search query text
        collection_id: ID of collection to search in
        resource_ids: Optional list of specific resources to search
        webhook_urls: Optional URLs to notify when search completes
        created_at: Timestamp when request was created
        status: Current status of the search request
        embedding: Optional embedding vector for the query
    """
    id: str
    query: str  
    collection_id: str
    filters: Optional[dict] = None
    resource_ids: Optional[List[str]] = None
    callback_urls: Optional[List[str]] = None
    webhook_urls: Optional[List[str]] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    embedding: Optional[List[float]] = None

@dataclass
class QueryType:
    """Defines how to process and execute a type of query

    Attributes:
        id: Unique identifier for the query type
        name: Display name of the query type
        prompt_template: Template for generating RAG prompts
        parameters: Optional configuration parameters
        description: Optional description of the query type
    """
    id: str
    name: str
    prompt_template: str
    parameters: Dict[str, str] = field(default_factory=dict)
    description: Optional[str] = None
@dataclass
class SearchContext:
    id: str
    query: str
    collection_id: str
    resource_ids: Optional[List[str]] = None
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"

@dataclass
class SearchResult:
    id: str
    search_id: str
    content: str
    score: float
    created_at: datetime = field(default_factory=datetime.now)
@dataclass
class SectionHeader:
    """Represents a section header in a document"""
    id: str
    heading: str

@dataclass
class ResourceChunk:
    """Represents a chunk of text from a resource with metadata"""
    id: str
    resource_id: str
    text: str
    sequence: int
    extract: str
    metadata: Optional[Dict[str, str]] = None
    path: Optional[List[SectionHeader]] = None
    preamble: Optional[str] = None
    postamble: Optional[str] = None
    score: Optional[float] = None
