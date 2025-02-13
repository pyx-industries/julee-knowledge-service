import unittest
from uuid import UUID
from datetime import datetime

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockCollectionRepository
)

class TestDeleteCollection(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.collection_repo = MockCollectionRepository()

        # Create test collection
        self.test_collection = domain.Collection(
            id="test-collection-1",
            name="Test Collection",
            subscription_id=UUID("00000000-0000-0000-0000-000000000000"),
            resource_types=[domain.ResourceType(id="test-type", name="Test Type", tooltip="Test Type")],
            description="Test Description"
        )
        self.collection_repo.collections[self.test_collection.id] = self.test_collection

        # Initialize usecase
        self.usecase = usecases.DeleteCollection({
            "collection_repository": self.collection_repo
        })

    def test_successful_deletion(self):
        result = self.usecase.execute(self.test_collection.id)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.id, str(self.test_collection.id))
        self.assertIsInstance(result.timestamp, datetime)

    def test_collection_not_found(self):
        non_existent_id = "non-existent-id"
        result = self.usecase.execute(non_existent_id)
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.id, str(non_existent_id))
        self.assertIn("not found", result.message.lower())

    def test_delete_already_deleted(self):
        # Delete once
        self.usecase.execute(self.test_collection.id)
        # Try to delete again
        result = self.usecase.execute(self.test_collection.id)
        self.assertEqual(result.status, "failed")
        self.assertIn("not found", result.message.lower())
