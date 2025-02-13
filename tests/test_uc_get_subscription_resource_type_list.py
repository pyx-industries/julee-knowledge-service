import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSubscriptionRepository,
    MockResourceTypeRepository
)

class TestGetSubscriptionResourceTypeList(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.subscription_repo = MockSubscriptionRepository()
        self.resource_type_repo = MockResourceTypeRepository()

        # Create test subscription
        # Create test resource types first
        self.test_resource_types = [
            domain.ResourceType(
                id="11111111-1111-1111-1111-111111111111",
                name="Test Type 1",
                tooltip="Test tooltip 1"
            ),
            domain.ResourceType(
                id="22222222-2222-2222-2222-222222222222",
                name="Test Type 2",
                tooltip="Test tooltip 2" 
            )
        ]

        # Create subscription with resource types
        self.test_subscription = domain.Subscription(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="Test Subscription",
            resource_types=self.test_resource_types,
            collections=[],
            is_active=True
        )
        self.subscription_repo.subscriptions[self.test_subscription.id] = self.test_subscription

        # Create test resource types
        self.test_resource_types = [
            domain.ResourceType(
                id="test-type-1",
                name="Test Type 1",
                tooltip="Test tooltip 1"
            ),
            domain.ResourceType(
                id="test-type-2",
                name="Test Type 2",
                tooltip="Test tooltip 2"
            )
        ]
        for rt in self.test_resource_types:
            self.resource_type_repo.resource_types[rt.id] = rt

        # Initialize usecase
        self.usecase = usecases.GetSubscriptionResourceTypeList({
            "subscription_repository": self.subscription_repo,
            "resource_type_repository": self.resource_type_repo
        })

    def test_successful_get_resource_types(self):
        result = self.usecase.execute(self.test_subscription.id)
        self.assertIsNotNone(result)
        self.assertEqual(len(result.resource_types), 2)
        self.assertEqual(result.resource_types[0].name, "Test Type 1")
        self.assertEqual(result.resource_types[1].name, "Test Type 2")

    def test_subscription_not_found(self):
        non_existent_id = UUID("11111111-1111-1111-1111-111111111111")
        result = self.usecase.execute(non_existent_id)
        self.assertIsNone(result)

    def test_invalid_subscription_id(self):
        with self.assertRaises(ValueError):
            self.usecase.execute("invalid-uuid")

    def test_subscription_with_no_resource_types(self):
        # Create subscription with no resource types
        empty_subscription = domain.Subscription(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            name="Empty Subscription",
            resource_types=[],
            collections=[],
            is_active=True 
        )
        self.subscription_repo.subscriptions[empty_subscription.id] = empty_subscription

        result = self.usecase.execute(empty_subscription.id)
        self.assertEqual(len(result.resource_types), 0)
