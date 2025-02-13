import unittest
from uuid import UUID

from knowledge_service import domain, usecases, interfaces
from knowledge_service.tests.mock_repos import (
    MockSubscriptionRepository,
    MockCollectionRepository
)

class TestPostNewCollectionToSubscription(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.subscription_repo = MockSubscriptionRepository()
        self.collection_repo = MockCollectionRepository()

        # Create test resource types
        self.test_resource_types = [
            domain.ResourceType(id="test-type-1", name="Test Type 1", tooltip="Test tooltip 1"),
            domain.ResourceType(id="test-type-2", name="Test Type 2", tooltip="Test tooltip 2")
        ]

        # Create test subscription
        self.test_subscription = domain.Subscription(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="Test Subscription",
            resource_types=self.test_resource_types,
            is_active=True,
            collections=[]
        )
        self.subscription_repo.subscriptions[self.test_subscription.id] = self.test_subscription

        # Initialize usecase
        self.usecase = usecases.PostNewCollectionToSubscription({
            "subscription_repository": self.subscription_repo,
            "collection_repository": self.collection_repo
        })

    def test_successful_collection_creation(self):
        new_collection_request = interfaces.requests.NewCollectionRequest(
            name="Test Collection",
            resource_type_ids=["test-type-1"],
            description="Test Description"
        )

        result = self.usecase.execute(self.test_subscription.id, new_collection_request)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Test Collection")
        self.assertEqual(result.num_resources, 0)

    def test_duplicate_collection_name(self):
        # Create first collection
        new_collection_request = interfaces.requests.NewCollectionRequest(
            name="Test Collection",
            resource_type_ids=["test-type-1"],
            description="Test Description"
        )
        self.usecase.execute(self.test_subscription.id, new_collection_request)

        # Try to create collection with same name
        result = self.usecase.execute(self.test_subscription.id, new_collection_request)
        self.assertIsNone(result)

    def test_invalid_resource_types(self):
        new_collection_request = interfaces.requests.NewCollectionRequest(
            name="Test Collection",
            resource_type_ids=["invalid-type"],
            description="Test Description"
        )

        with self.assertRaises(ValueError):
            self.usecase.execute(self.test_subscription.id, new_collection_request)

    def test_subscription_not_found(self):
        non_existent_id = UUID("11111111-1111-1111-1111-111111111111")
        new_collection_request = interfaces.requests.NewCollectionRequest(
            name="Test Collection",
            resource_type_ids=["test-type-1"],
            description="Test Description"
        )

        with self.assertRaises(Exception):
            self.usecase.execute(non_existent_id, new_collection_request)
