import unittest
from datetime import datetime
from typing import List, Optional

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSearchRepository,
    MockGraphRepository,
    MockLanguageModelRepository
)

class TestMockGraphRepository(MockGraphRepository):
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

        # Sort chunks by score in descending order
        chunks.sort(key=lambda x: x.score, reverse=True)
        return chunks

class TestIdentifyRelatedContent(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.search_repo = MockSearchRepository()
        self.graph_repo = TestMockGraphRepository()
        self.language_model_repo = MockLanguageModelRepository()

        # Create test search request
        self.test_search_request = domain.SearchRequest(
            id="search-1",
            collection_id="test-collection",
            query="test query",
            filters={},
            created_at=datetime.now()
        )
        self.search_repo.search_requests[self.test_search_request.id] = self.test_search_request

        # Create test chunks with embeddings
        self.test_chunks = [
            domain.ResourceChunk(
                id="chunk-1",
                resource_id="test-resource-1",
                text="Relevant content 1",
                sequence=1,
                extract="Relevant content 1",
                metadata={"embedding": [0.1, 0.2, 0.3]}
            ),
            domain.ResourceChunk(
                id="chunk-2",
                resource_id="test-resource-1",
                text="Relevant content 2",
                sequence=2,
                extract="Relevant content 2", 
                metadata={"embedding": [0.4, 0.5, 0.6]} 
            )
        ]
        self.graph_repo.nodes.update({chunk.id: chunk for chunk in self.test_chunks})

        # Initialize usecase
        self.usecase = usecases.IdentifyRelatedContent({
            "search_repository": self.search_repo,
            "graph_repository": self.graph_repo,
            "language_model_repository": self.language_model_repo
        })

    def test_successful_content_identification(self):
        result = self.usecase.execute(self.test_search_request.id)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.search_id, self.test_search_request.id)
        self.assertTrue(len(result.related_chunks) > 0)
        # Verify chunks were scored and ranked
        self.assertTrue(all(hasattr(chunk, 'score') for chunk in result.related_chunks))
        self.assertTrue(result.related_chunks[0].score >= result.related_chunks[1].score)

    def test_search_request_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("not found", result.message.lower())

    def test_no_chunks_found(self):
        # Clear chunks from graph
        self.graph_repo.nodes.clear()

        result = self.usecase.execute(self.test_search_request.id)
        self.assertFalse(result.success)
        self.assertIn("no relevant content found", result.message.lower())

    def test_with_filters(self):
        # Add filters to search request
        filtered_request = self.test_search_request
        filtered_request.filters = {"resource_type": "document"}
        # Add resource type to chunk metadata
        for chunk in self.test_chunks:
            chunk.metadata["resource_type"] = "document"
        self.search_repo.search_requests[filtered_request.id] = filtered_request

        result = self.usecase.execute(filtered_request.id)
        self.assertTrue(result.success)
        # Verify filters were applied in chunk selection
        self.assertTrue(all(
            chunk.metadata.get("resource_type") == "document"
            for chunk in result.related_chunks
        ))

    def test_similarity_calculation_error(self):
        # Mock similarity calculation error
        def mock_similarity_error(*args):
            raise Exception("Similarity calculation failed")

        self.graph_repo.calculate_chunk_similarities = mock_similarity_error

        result = self.usecase.execute(self.test_search_request.id)
        self.assertFalse(result.success)
        self.assertIn("similarity calculation failed", result.message.lower())
