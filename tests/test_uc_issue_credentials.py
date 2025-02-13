import unittest
from datetime import datetime
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSearchRepository,
    MockGraphRepository,
    MockLanguageModelRepository
)

class TestIssueCredentials(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.search_repo = MockSearchRepository()
        self.graph_repo = MockGraphRepository()
        self.language_model_repo = MockLanguageModelRepository()

        # Create test search request and results
        self.test_search_request = domain.SearchRequest(
            id="search-1",
            collection_id="test-collection",
            query="test query",
            filters={},
            created_at=datetime.now()
        )
        self.search_repo.search_requests[self.test_search_request.id] = self.test_search_request

        self.test_search_results = [
            domain.SearchResult(
                id="result-1",
                search_id=self.test_search_request.id,
                content="Test result 1",
                score=0.9,
                created_at=datetime.now()
            ),
            domain.SearchResult(
                id="result-2",
                search_id=self.test_search_request.id,
                content="Test result 2",
                score=0.8,
                created_at=datetime.now()
            )
        ]
        self.search_repo.save_search_results(
            self.test_search_request.id,
            self.test_search_results
        )

        # Initialize usecase
        self.usecase = usecases.IssueCredentials({
            "search_repository": self.search_repo,
            "graph_repository": self.graph_repo,
            "language_model_repository": self.language_model_repo
        })

    def test_successful_credential_issuance(self):
        result = self.usecase.execute(self.test_search_request.id)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.credential_id)
        self.assertIsInstance(result.timestamp, datetime)
        self.assertTrue(result.credential_url.startswith("http"))

    def test_search_request_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("not found", result.message.lower())

    def test_no_search_results(self):
        # Create search request with no results
        empty_search = domain.SearchRequest(
            id="empty-search", 
            collection_id="test-collection", 
            query="test query", 
            filters={}, 
            created_at=datetime.now()
        ) 
        self.search_repo.search_requests[empty_search.id] = empty_search

        result = self.usecase.execute(empty_search.id)
        self.assertFalse(result.success)
        self.assertIn("no search results found", result.message.lower())

    def test_graph_error(self):
        # Mock graph error
        def mock_graph_error(*args):
            raise Exception("graph error")

        self.language_model_repo.generate_credential = mock_graph_error

        result = self.usecase.execute(self.test_search_request.id)
        self.assertFalse(result.success)
        self.assertIn("graph error", result.message)

    def test_credential_generation_error(self):
        # Mock credential generation error
        def mock_credential_error(*args):
            raise Exception("Credential generation failed")

        self.language_model_repo.generate_credential = mock_credential_error

        result = self.usecase.execute(self.test_search_request.id)
        self.assertFalse(result.success)
        self.assertIn("credential generation failed", result.message.lower())
