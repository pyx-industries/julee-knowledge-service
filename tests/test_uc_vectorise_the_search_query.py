import unittest
from datetime import datetime
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSearchRepository,
    MockLanguageModelRepository,
    MockGraphRepository
)

class TestVectoriseTheSearchQuery(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.search_repo = MockSearchRepository()
        self.language_model_repo = MockLanguageModelRepository()
        self.graph_repo = MockGraphRepository()

        # Create test search request
        self.test_search_request = domain.SearchRequest(
            id="search-1",
            collection_id="test-collection",
            query="test query",
            filters={},
            timestamp=datetime.now()
        )
        self.search_repo.search_requests[self.test_search_request.id] = self.test_search_request

        # Initialize usecase
        self.usecase = usecases.VectoriseTheSearchQuery({
            "search_repository": self.search_repo,
            "language_model_repository": self.language_model_repo,
            "graph_repository": self.graph_repo
        })

    def test_successful_vectorisation(self):
        result = self.usecase.execute(self.test_search_request.id)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.search_id, self.test_search_request.id)
        # Verify vector was generated and stored
        self.assertTrue(len(self.language_model_repo.embeddings) > 0)
        self.assertTrue(self.graph_repo.check_search_vector_exists(self.test_search_request.id))

    def test_search_request_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("not found", result.message.lower())

    def test_empty_query(self):
        # Create search request with empty query
        empty_query_request = self.test_search_request
        empty_query_request.query = ""
        self.search_repo.search_requests[empty_query_request.id] = empty_query_request

        result = self.usecase.execute(empty_query_request.id)
        self.assertFalse(result.success)
        self.assertIn("empty query", result.message.lower())

    def test_embedding_generation_error(self):
        # Mock embedding error
        def mock_embedding_error(text):
            raise Exception("Embedding generation failed")

        self.language_model_repo.generate_embedding = mock_embedding_error

        result = self.usecase.execute(self.test_search_request.id)
        self.assertFalse(result.success)
        self.assertIn("embedding generation failed", result.message.lower())

    def test_graph_storage_error(self):
        # Mock graph storage error
        def mock_storage_error(search_id, vector):
            raise Exception("Graph storage failed")

        self.graph_repo.store_search_vector = mock_storage_error

        result = self.usecase.execute(self.test_search_request.id)
        self.assertFalse(result.success)
        self.assertIn("graph storage failed", result.message.lower())
