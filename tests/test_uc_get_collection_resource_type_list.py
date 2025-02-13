import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockCollectionRepository,
    MockResourceTypeRepository
)

class TestGetCollectionResourceTypeList(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.collection_repo = MockCollectionRepository()
        self.resource_type_repo = MockResourceTypeRepository()

        # Create test resource types
        self.test_resource_types = [
            domain.ResourceType(id="00000000-0000-0000-0000-000000000001", name="Test Type 1", tooltip="Test tooltip 1"),
            domain.ResourceType(id="00000000-0000-0000-0000-000000000002", name="Test Type 2", tooltip="Test tooltip 2")
        ]

        # Create test collection
        self.test_collection = domain.Collection(
            id="test-collection-1",
            name="Test Collection",
            subscription_id=UUID("00000000-0000-0000-0000-000000000000"),
            resource_types=self.test_resource_types,
            description="Test Description"
        )
        self.collection_repo.collections[self.test_collection.id] = self.test_collection
        for rt in self.test_resource_types:
            self.resource_type_repo.resource_types[rt.id] = rt

        # Initialize usecase
        self.usecase = usecases.GetCollectionResourceTypeList({
            "collection_repository": self.collection_repo,
            "resource_type_repository": self.resource_type_repo
        })

    def test_successful_get_resource_types(self):
        result = self.usecase.execute(self.test_collection.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.resource_types), 2)
        self.assertEqual(result.resource_types[0].name, "Test Type 1")
        self.assertEqual(result.resource_types[1].name, "Test Type 2")

    def test_collection_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNone(result)

    def test_empty_resource_type_list(self):
        # Create collection with no resource types
        empty_collection = domain.Collection(
            id="empty-collection", 
            name="Empty Collection", 
            subscription_id=UUID("00000000-0000-0000-0000-000000000000"), 
            resource_types=[],
            description="Empty Collection" 
        )
        self.collection_repo.collections[empty_collection.id] = empty_collection

        result = self.usecase.execute(empty_collection.id)
        self.assertEqual(len(result.resource_types), 0)
