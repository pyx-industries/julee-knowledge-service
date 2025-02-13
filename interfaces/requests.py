"""
Request interface definitions for the knowledge service.

This module contains all request data models used by the service endpoints
and use cases. These models define the structure of incoming data.
"""

from enum import Enum
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel


class NewResourceQueryRequest(BaseModel):
    """Request to create a new resource query."""

    query: str


class SubscriptionStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class NewSubscriptionRequest(BaseModel):
    """Request to create a new subscription."""

    name: str
    resource_type_ids: List[str]
    status: SubscriptionStatus


class NewCollectionRequest(BaseModel):
    """Request to create a new collection within a subscription."""

    name: str
    resource_type_ids: List[str]
    description: Optional[str] = None


class ResourceUploadRequest(BaseModel):
    """Request to upload a new resource to a collection."""

    collection_id: str
    resource_type_id: str
    file_name: str
    file_content: bytes
    name: Optional[str]
    webhooks: List[str] = []


class QueryCollectionRequest(BaseModel):
    """Request to query across a collection."""

    prompt: str


class QueryResourceRequest(BaseModel):
    """Request to query a specific resource."""

    prompt: str
    resource_ids: list[int] = []


# class QueryCollectionRequest(BaseModel):
#     """Request to query across a collection."""

#     prompt: str
#     resource_ids: Optional[List[int]] = []


# class ResourceUploadRequest(BaseModel):
#     """Request to upload a new resource."""

#     file_name: str
#     file_content: bytes
#     collection_id: UUID
#     resource_type_id: UUID
#     webhooks: Optional[List[HttpUrl]]
#     name: str


class QueryTriple(BaseModel):
    """A triple pattern for querying."""

    subject: Optional[str]
    predicate: Optional[str]
    object: Optional[str]


class QueryParameters(BaseModel):
    """Parameters for controlling query behavior."""

    max_results: Optional[int]
