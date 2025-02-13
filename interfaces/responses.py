"""
Response interface definitions for the knowledge service.

This module contains all response data models used by the service endpoints
and use cases. These models define the structure of outgoing data.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from typing import List, Optional
from typing import List, Optional
from uuid import UUID
from enum import Enum
from knowledge_service import domain

from pydantic import BaseModel, HttpUrl, AnyUrl, validator

class ResourceTypeResponse(BaseModel):
    id: str
    name: str
    tooltip: str

class SubscriptionStatus(str, Enum):
    """Status values for subscriptions"""
    active = "active"
    inactive = "inactive"

class SubscriptionResponse(BaseModel):
    """Response containing subscription details."""
    id: str
    name: str
    status: SubscriptionStatus
    resource_types: List[ResourceTypeResponse]


class SubscriptionListResponse(BaseModel):
    """Response containing list of subscriptions."""

    subscriptions: list[SubscriptionResponse]


class ResourceTypeListResponse(BaseModel):
    """Response containing available resource types."""

    resource_types: list[ResourceTypeResponse]


class CollectionResponse(BaseModel):
    """Response containing collection details."""

    id: str
    name: str
    subscription_id: UUID
    num_resources: int = 0


class CollectionListResponse(BaseModel):
    """Response containing list of collections."""

    collections: list[CollectionResponse]


class DeleteSubscriptionResponse(BaseModel):
    """Response for subscription deletion."""

    id: str
    success: bool
    message: Optional[str] = None


class DeleteCollectionResponse(BaseModel):
    """Response for collection deletion."""

    id: str
    status: str
    message: Optional[str]
    timestamp: datetime


class ProcessingStatus(str, Enum):
    """Standard status values for processing operations"""
    pending = "pending"
    processing = "processing"
    completed = "completed" 
    failed = "failed"

class ResourceResponse(BaseModel):
    """Response containing resource details."""
    id: UUID
    name: str
    resource_type_id: str
    collection_id: str
    status: ProcessingStatus
    file_type: Optional[str]
    markdown_content: Optional[str]
    file: Optional[bytes] = None
    file_type: Optional[str]
    markdown_content: Optional[str]


class ResourceListResponse(BaseModel):
    """Response containing list of subscriptions."""

    resources: list[ResourceResponse]


class ResourceMetadataResponse(BaseModel):
    """Response containing resource metadata."""

    id: UUID
    metadata: dict


class DeleteResourceResponse(BaseModel):
    """Response for resource deletion."""

    id: str
    success: bool
    message: Optional[str] = None
    timestamp: datetime

class QueryCollectionResponse(BaseModel):
    """Response for collection queries."""

    results: list[str]


class QueryResourceResponse(BaseModel):
    """Response for resource queries."""

    results: list[str]


class QueryResult(BaseModel):
    """Detailed query result."""

    content: str
    score: float


class QueryResultMetadata(BaseModel):
    """Metadata about a query result."""

    search_id: str
    query: str
    timestamp: datetime
    filters: Optional[dict] = None
    version_of_model: str


class ResourceQueryResponse(BaseModel):
    """Response for resource queries."""

    results: list[QueryResult]


class ResourceUploadResponse(BaseModel):
    """Response for resource upload."""
    resource_id: str
    status: ProcessingStatus
    resource_url: HttpUrl
    message: Optional[str] = None
    message: Optional[str] = None
    message: Optional[str] = None
    webhooks: List[str] = []


class IssueCredentialsResponse(BaseModel):
    """Response for credential issuance."""

    success: bool
    credential_id: UUID
    message: Optional[str]
    credential_url: Optional[str] = None
    timestamp: Optional[datetime] = None


# class ResourceUploadResponse(BaseModel):
#     """Response for resource upload."""

# #     resource_id: UUID
#     resource_url: HttpUrl
#     message: Optional[str] = None
#     webhooks: List[HttpUrl]


class ResourceProcessingResponse(BaseModel):
    """Response for resource processing status updates."""
    resource_id: UUID
    status: ProcessingStatus
    stage: str
    message: Optional[str] = None
    timestamp: datetime = datetime.now()

class ChunkResponse(BaseModel):
    """Response containing chunk details."""
    id: UUID
    resource_id: UUID
    sequence: int
    content: str
    embedding: Optional[List[float]] = None

class SearchRequestResponse(BaseModel):
    """Response for search request initiation/status."""
    search_id: UUID
    status: ProcessingStatus
    created_at: datetime = datetime.now()
    message: Optional[str] = None

class WebhookCallbackResponse(BaseModel):
    """Standard response format for webhook callbacks."""
    event_type: str
    resource_id: Optional[UUID] = None
    search_id: Optional[UUID] = None
    status: ProcessingStatus
    timestamp: datetime = datetime.now()
    message: Optional[str] = None

class ResourceUploadProcessComplete(BaseModel):
    """Response when resource upload processing is complete."""
    resource_url: HttpUrl
    message: Optional[str] = None


class InitiateSearchResponse(BaseModel):
    """Response when search is initiated."""

    success: bool
    search_url: str
    message: Optional[str] = None


class VectoriseSearchResponse(BaseModel):
    """Response when search vectorization is complete."""

    search_url: HttpUrl
    message: Optional[str] = None


class IdentifyRelatedContentResponse(BaseModel):
    """Response when related content is identified."""

    success: bool
    search_id: str
    search_url: str  # Changed from HttpUrl to str to allow relative URLs
    message: Optional[str] = None
    related_chunks: Optional[List[domain.ResourceChunk]] = None


class ExecuteTheRagResponse(BaseModel):
    """Response when RAG execution is complete."""

    success: bool
    search_url: Optional[str] = None
    message: Optional[str] = None
    prompt: Optional[str] = None
    context_chunks: Optional[List[str]] = None
class SubscriptionStatus(str, Enum):
    """Status values for subscriptions"""
    active = "active"
    inactive = "inactive"

