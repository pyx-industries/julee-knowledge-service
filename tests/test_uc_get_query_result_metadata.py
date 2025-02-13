import unittest
from uuid import UUID
from datetime import datetime

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSearchRepository
)

class TestGetQueryResultMetadata(unittest.TestCase):
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

        # Initialize usecase
        self.usecase = usecases.GetQueryResultMetadata({
            "search_repository": self.search_repo
        })

    def test_successful_get_metadata(self):
        result = self.usecase.execute(self.test_search_request.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.search_id, self.test_search_request.id)
        self.assertEqual(result.query, self.test_search_request.query)
        self.assertEqual(result.timestamp, self.test_search_request.created_at)

    def test_search_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNone(result)

    def test_with_filters(self):
        # Create search request with filters
        filtered_search = domain.SearchRequest(
            id="filtered-search",
            collection_id="test-collection",
            query="filtered query",
            filters={"date": "2024-01-01"},
            created_at=datetime.now()
        )
        self.search_repo.search_requests[filtered_search.id] = filtered_search

        result = self.usecase.execute(filtered_search.id)
        self.assertEqual(result.filters, filtered_search.filters)
