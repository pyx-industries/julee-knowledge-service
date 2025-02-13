import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSubscriptionRepository
)

class TestGetSubscriptionList(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.subscription_repo = MockSubscriptionRepository()

        # Create test subscriptions
        # Create test resource types
        self.test_resource_types_1 = [
            domain.ResourceType(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                name="Test Type 1",
                tooltip="Test tooltip 1"
            )
        ]
        self.test_resource_types_2 = [
            domain.ResourceType(
                id=UUID("22222222-2222-2222-2222-222222222222"),
                name="Test Type 2",
                tooltip="Test tooltip 2"
            )
        ]

        # Create test subscriptions with proper resource types
        self.test_subscriptions = [
            domain.Subscription(
                id=UUID("00000000-0000-0000-0000-000000000000"),
                name="Test Subscription 1",
                resource_types=self.test_resource_types_1,
                collections=[],
                is_active=True
            ),
            domain.Subscription(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                name="Test Subscription 2", 
                resource_types=self.test_resource_types_2,
                collections=[],
                is_active=False
            )
        ]

        for sub in self.test_subscriptions:
            self.subscription_repo.subscriptions[sub.id] = sub

        # Initialize usecase
        self.usecase = usecases.GetSubscriptionList({
            "subscription_repository": self.subscription_repo
        })

    def test_get_all_subscriptions(self):
        # Execute usecase
        result = self.usecase.execute()

        # Verify response
        self.assertIsNotNone(result)
        self.assertEqual(len(result.subscriptions), 2)

        # Verify subscription details
        self.assertEqual(result.subscriptions[0].name, "Test Subscription 1")
        self.assertEqual(result.subscriptions[0].status, "active")
        self.assertEqual(result.subscriptions[1].name, "Test Subscription 2")
        self.assertEqual(result.subscriptions[1].status, "inactive")

    def test_empty_subscription_list(self):
        # Clear subscriptions
        self.subscription_repo.subscriptions.clear()

        result = self.usecase.execute()
        self.assertEqual(len(result.subscriptions), 0)
