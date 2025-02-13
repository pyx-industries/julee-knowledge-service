import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockTaskDispatchRepository,
    MockResourceRepository
)

class TestVentilateResourceProcessing(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.dispatch_repo = MockTaskDispatchRepository()
        self.resource_repo = MockResourceRepository()

        # Create test resource
        self.test_resource = domain.Resource(
            id="test-resource-1",
            collection_id="test-collection",
            resource_type_id="test-type",
            name="Test Resource",
            file_name="test.txt",
            file=b"Test content",
            file_type="text/plain",
            markdown_content="Test content",
            callback_urls=["http://callback1.test", "http://callback2.test"]
        )
        self.resource_repo.resources[self.test_resource.id] = self.test_resource

        # Initialize usecase
        self.usecase = usecases.VentilateResourceProcessing({
            "task_dispatch_repository": self.dispatch_repo,
            "resource_repository": self.resource_repo
        })

    def test_successful_ventilation(self):
        # Execute usecase
        result = self.usecase.execute(self.test_resource.id)

        # Verify interactions
        self.assertIsInstance(result, list)
        # Verify callbacks were sent
        self.assertEqual(len(self.dispatch_repo.notifications), 1)

    def test_resource_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertEqual(result, [])

    def test_no_callback_urls(self):
        # Modify resource to have no callbacks
        resource_no_callbacks = self.test_resource
        resource_no_callbacks.callback_urls = []
        self.resource_repo.resources[resource_no_callbacks.id] = resource_no_callbacks

        result = self.usecase.execute(resource_no_callbacks.id)
        self.assertEqual(result, [])
        self.assertEqual(len(self.dispatch_repo.notifications), 0)

    def test_callback_error(self):
        # Mock callback error
        def mock_callback_error(resource_id):
            raise Exception("Callback failed")

        self.dispatch_repo.send_quarantine_notification = mock_callback_error

        with self.assertRaises(Exception) as context:
            self.usecase.execute(self.test_resource.id)

    def test_duplicate_callback_urls(self):
        # Modify resource to have duplicate callbacks
        resource_dup_callbacks = self.test_resource
        resource_dup_callbacks.callback_urls = ["http://test.com", "http://test.com"]
        self.resource_repo.resources[resource_dup_callbacks.id] = resource_dup_callbacks

        result = self.usecase.execute(resource_dup_callbacks.id)
        # Should only send one notification even with duplicate URLs
        self.assertEqual(len(self.dispatch_repo.notifications), 1)
