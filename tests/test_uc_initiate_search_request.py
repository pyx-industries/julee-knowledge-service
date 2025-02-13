import unittest
from uuid import UUID
from datetime import datetime

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockTaskDispatchRepository,
    MockSearchRepository
)

class TestInitiateSearchRequest(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.task_dispatch_repo = MockTaskDispatchRepository()
        self.search_repo = MockSearchRepository()

        # Create test search request
        self.test_search_request = domain.SearchRequest(
            id="search-1",
            collection_id="test-collection",
            query="test query",
            filters={},
            created_at=datetime.now()
        )
        self.search_repo.search_requests[self.test_search_request.id] = self.test_search_request

        # Initialize usecase
        self.usecase = usecases.InitiateSearchRequest({
            "task_dispatch_repository": self.task_dispatch_repo,
            "search_repository": self.search_repo
        })

    def test_successful_initiation(self):
        result = self.usecase.execute(self.test_search_request.id)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertEqual(result.search_url, f"/search/{self.test_search_request.id}")
        # Verify task was dispatched
        self.assertEqual(len(self.task_dispatch_repo.notifications), 1)

    def test_search_request_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertEqual(len(self.task_dispatch_repo.notifications), 0)

    def test_task_dispatch_error(self):
        # Mock dispatch error
        def mock_dispatch_error(*args):
            raise Exception("Task dispatch failed")

        self.task_dispatch_repo.send_quarantine_notification = mock_dispatch_error

        result = self.usecase.execute(self.test_search_request.id)
        self.assertIsNotNone(result)
        self.assertFalse(result.success)
        self.assertIn("dispatch failed", result.message.lower())
