import unittest
from datetime import datetime
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockTaskDispatchRepository,
    MockSearchRepository
)

class TestVentilateSearchResults(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.dispatch_repo = MockTaskDispatchRepository()
        self.search_repo = MockSearchRepository()

        # Create test search request and results
        self.test_search_request = domain.SearchRequest(
            id="search-1",
            collection_id="test-collection",
            query="test query",
            filters={},
            timestamp=datetime.now()
        )
        self.search_repo.search_requests[self.test_search_request.id] = self.test_search_request

        self.test_search_results = [
            domain.SearchResult(
                id="result-1",
                search_id=self.test_search_request.id,
                chunk_id="chunk-1",
                score=0.9,
                text="Test result 1"
            ),
            domain.SearchResult(
                id="result-2",
                search_id=self.test_search_request.id,
                chunk_id="chunk-2", 
                score=0.8,
                text="Test result 2"
            )
        ]
        self.search_repo.save_search_results(
            self.test_search_request.id,
            self.test_search_results
        )

        # Initialize usecase
        self.usecase = usecases.VentilateSearchResults({
            "task_dispatch_repository": self.dispatch_repo,
            "search_repository": self.search_repo
        })

    def test_successful_ventilation(self):
        # Execute usecase
        result = self.usecase.execute(self.test_search_request.id)

        # Verify interactions
        self.assertIsNone(result)
        # Verify notifications were sent
        self.assertEqual(len(self.dispatch_repo.notifications), 1)

    def test_search_request_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNone(result)
        self.assertEqual(len(self.dispatch_repo.notifications), 0)

    def test_no_search_results(self):
        # Create search request with no results
        empty_search = domain.SearchRequest(
            id="empty-search",
            collection_id="test-collection",
            query="test query",
            filters={},
            timestamp=datetime.now()
        )
        self.search_repo.search_requests[empty_search.id] = empty_search

        result = self.usecase.execute(empty_search.id)
        self.assertIsNone(result)
        self.assertEqual(len(self.dispatch_repo.notifications), 0)
import unittest
from datetime import datetime
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockTaskDispatchRepository,
    MockSearchRepository
)

class TestVentilateSearchResults(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.dispatch_repo = MockTaskDispatchRepository()
        self.search_repo = MockSearchRepository()

        # Create test search request and results
        self.test_search_request = domain.SearchRequest(
            id="search-1",
            collection_id="test-collection",
            query="test query",
            filters={},
            timestamp=datetime.now(),
            callback_urls=["http://test.com/callback"]
        )
        self.search_repo.search_requests[self.test_search_request.id] = self.test_search_request

        self.test_search_results = [
            domain.SearchResult(
                id="result-1",
                search_id=self.test_search_request.id,
                chunk_id="chunk-1",
                score=0.9,
                text="Test result 1"
            ),
            domain.SearchResult(
                id="result-2",
                search_id=self.test_search_request.id,
                chunk_id="chunk-2",
                score=0.8,
                text="Test result 2"
            )
        ]
        self.search_repo.save_search_results(
            self.test_search_request.id,
            self.test_search_results
        )

        # Initialize usecase
        self.usecase = usecases.VentilateSearchResults({
            "task_dispatch_repository": self.dispatch_repo,
            "search_repository": self.search_repo
        })

    def test_successful_ventilation(self):
        # Execute usecase
        result = self.usecase.execute(self.test_search_request.id)

        # Verify response
        self.assertIsNone(result)
        # Verify callbacks were sent
        self.assertEqual(len(self.dispatch_repo.notifications), 1)

    def test_search_request_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNone(result)
        self.assertEqual(len(self.dispatch_repo.notifications), 0)

    def test_no_callback_urls(self):
        # Create search request with no callbacks
        request_no_callbacks = self.test_search_request
        request_no_callbacks.callback_urls = []
        self.search_repo.search_requests[request_no_callbacks.id] = request_no_callbacks

        result = self.usecase.execute(request_no_callbacks.id)
        self.assertIsNone(result)
        self.assertEqual(len(self.dispatch_repo.notifications), 0)

    def test_callback_error(self):
        # Mock callback error
        def mock_callback_error(*args):
            raise Exception("Callback failed")

        self.dispatch_repo.send_search_notification = mock_callback_error

        with self.assertRaises(Exception) as context:
            self.usecase.execute(self.test_search_request.id)
        self.assertIn("callback failed", str(context.exception).lower())

    def test_duplicate_callback_urls(self):
        # Create search request with duplicate callbacks
        request_dup_callbacks = self.test_search_request
        request_dup_callbacks.callback_urls = ["http://test.com", "http://test.com"]
        self.search_repo.search_requests[request_dup_callbacks.id] = request_dup_callbacks

        result = self.usecase.execute(request_dup_callbacks.id)
        self.assertIsNone(result)
        # Should only send one notification even with duplicate URLs
        self.assertEqual(len(self.dispatch_repo.notifications), 1)
