from abc import ABC, abstractmethod
from typing import List
from ..domain.chunks import ResourceChunk

class GraphRepository(ABC):
    """Repository for graph database operations"""

    @abstractmethod
    def create_chunk_nodes(self, chunks: List[ResourceChunk]) -> None:
        """Create nodes in the graph database for resource chunks

        Args:
            chunks: List of resource chunks to create nodes for
        """
