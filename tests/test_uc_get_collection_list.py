import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSubscriptionRepository,
    MockCollectionRepository,
    MockResourceRepository
)

class TestGetCollectionList(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.subscription_repo = MockSubscriptionRepository()
        self.collection_repo = MockCollectionRepository()
        self.resource_repo = MockResourceRepository()

        # Create test resource type
        self.test_resource_type = domain.ResourceType(id="test-type", name="Test Type", tooltip="Test tooltip")

        # Create test subscription
        self.test_subscription = domain.Subscription(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="Test Subscription",
            resource_types=[self.test_resource_type],
            is_active=True,
            collections=[]
        )
        self.subscription_repo.subscriptions[self.test_subscription.id] = self.test_subscription

        # Create test collections
        self.test_collections = [
            domain.Collection(
                id="test-collection-1",
                name="Test Collection 1", 
                subscription_id=self.test_subscription.id,
                resource_types=[self.test_resource_type],
                description="Test Description 1"
            ),
            domain.Collection(
                id="test-collection-2",
                name="Test Collection 2", 
                subscription_id=self.test_subscription.id,
                resource_types=[self.test_resource_type],
                description="Test Description 2"
            )
        ]
        for collection in self.test_collections:
            self.collection_repo.collections[collection.id] = collection

        # Initialize usecase
        self.usecase = usecases.GetCollectionList({
            "subscription_repository": self.subscription_repo,
            "collection_repository": self.collection_repo,
            "resource_repository": self.resource_repo
        })

    def test_successful_get_collections(self):
        result = self.usecase.execute(self.test_subscription.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.collections), 2)
        self.assertEqual(result.collections[0].name, "Test Collection 1")
        self.assertEqual(result.collections[1].name, "Test Collection 2")

    def test_subscription_not_found(self):
        non_existent_id = UUID("11111111-1111-1111-1111-111111111111")
        result = self.usecase.execute(non_existent_id)
        self.assertIsNone(result)

    def test_empty_collection_list(self):
        # Clear collections
        self.collection_repo.collections.clear()

        result = self.usecase.execute(self.test_subscription.id) 
        self.assertEqual(len(result.collections), 0)


