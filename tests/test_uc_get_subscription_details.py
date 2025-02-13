import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSubscriptionRepository,
    MockResourceTypeRepository
)

class TestGetSubscriptionDetails(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.subscription_repo = MockSubscriptionRepository()

        # Create test subscription
        # Create test resource types
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

        # Create test subscription with resource types
        self.test_subscription = domain.Subscription(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="Test Subscription", 
            resource_types=self.test_resource_types,
            collections=[],
            is_active=True
        )
        self.subscription_repo.subscriptions[self.test_subscription.id] = self.test_subscription

        # Initialize usecase
        self.usecase = usecases.GetSubscriptionDetails({
            "subscription_repository": self.subscription_repo
        })

    def test_successful_get_details(self):
        # Execute usecase
        result = self.usecase.execute(self.test_subscription.id)

        # Verify response
        self.assertIsNotNone(result)
        self.assertEqual(result.id, str(self.test_subscription.id))
        self.assertEqual(result.name, self.test_subscription.name)
        self.assertEqual(result.status, "active")

    def test_subscription_not_found(self):
        non_existent_id = UUID("11111111-1111-1111-1111-111111111111")
        result = self.usecase.execute(non_existent_id)
        self.assertIsNone(result)

    def test_inactive_subscription(self):
        # Create inactive subscription
        inactive_subscription = domain.Subscription(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            name="Inactive Subscription",
            resource_types=[
                domain.ResourceType(
                    id="33333333-3333-3333-3333-333333333333",
                    name="Test Type",
                    tooltip="Test tooltip"
                )
            ],
            collections=[],
            is_active=False
        )
        self.subscription_repo.subscriptions[inactive_subscription.id] = inactive_subscription

        result = self.usecase.execute(inactive_subscription.id)
        self.assertEqual(result.status, "inactive")
