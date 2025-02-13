import unittest
from uuid import UUID
from datetime import datetime

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSearchRepository
)

class TestGetQueryResult(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.search_repo = MockSearchRepository()

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
                score=0.9
            ),
            domain.SearchResult(
                id="result-2",
                search_id=self.test_search_request.id,
                content="Test result 2",
                score=0.8
            )
        ]
        self.search_repo.save_search_results(
            self.test_search_request.id,
            self.test_search_results
        )

        # Initialize usecase
        self.usecase = usecases.GetQueryResult({
            "search_repository": self.search_repo
        })

    def test_successful_get_results(self): 
        result = self.usecase.execute(self.test_search_request.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.results), 2)
        self.assertEqual(result.results[0].content, "Test result 1")
        self.assertEqual(result.results[1].content, "Test result 2")

    def test_search_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNone(result)

    def test_search_with_no_results(self):
        # Create search request with no results
        empty_search = domain.SearchRequest(
            id="empty-search",
            collection_id="test-collection",
            query="no results query",
            filters={},
            created_at=datetime.now()
        )
        self.search_repo.search_requests[empty_search.id] = empty_search

        result = self.usecase.execute(empty_search.id)
        self.assertEqual(len(result.results), 0)
