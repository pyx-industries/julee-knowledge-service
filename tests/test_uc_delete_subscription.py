import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSubscriptionRepository
)

class TestDeleteSubscription(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.subscription_repo = MockSubscriptionRepository()

        # Create test subscription
        self.test_subscription = domain.Subscription(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="Test Subscription",
            is_active=True,
            resource_types=[],
            collections=[]
        )
        self.subscription_repo.subscriptions[self.test_subscription.id] = self.test_subscription

        # Initialize usecase
        self.usecase = usecases.DeleteSubscription({
            "subscription_repository": self.subscription_repo
        })

    def test_successful_deletion(self):
        # Execute usecase
        result = self.usecase.execute(self.test_subscription.id)

        # Verify response
        self.assertTrue(result.success)
        self.assertEqual(result.id, str(self.test_subscription.id))
        self.assertNotIn(self.test_subscription.id, self.subscription_repo.subscriptions)

    def test_delete_non_existent(self):
        non_existent_id = UUID("11111111-1111-1111-1111-111111111111")
        result = self.usecase.execute(non_existent_id)

        self.assertFalse(result.success)
        self.assertEqual(result.id, str(non_existent_id))

