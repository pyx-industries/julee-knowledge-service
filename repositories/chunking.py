from abc import ABC, abstractmethod
from typing import List
from ..domain import ResourceType, Resource
from ..domain.chunks import ResourceChunk

class ChunkingRepository(ABC):
    """Repository for chunking resource content"""

    @abstractmethod
    def chunk_resource(
        self,
        resource_type: ResourceType,
        resource: Resource
    ) -> List[ResourceChunk]:
        """Split resource content into chunks based on resource type strategy"""
