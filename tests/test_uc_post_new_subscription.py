import unittest
from uuid import UUID

from knowledge_service import domain, usecases, interfaces
from knowledge_service.tests.mock_repos import (
    MockResourceTypeRepository,
    MockSubscriptionRepository
)

class TestPostNewSubscription(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.resource_type_repo = MockResourceTypeRepository()
        self.subscription_repo = MockSubscriptionRepository()

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
        self.usecase = usecases.PostNewSubscription({
            "resource_type_repository": self.resource_type_repo,
            "subscription_repository": self.subscription_repo
        })

    def test_successful_subscription_creation(self):
        new_subscription_request = interfaces.requests.NewSubscriptionRequest(
            name="Test Subscription",
            resource_type_ids=["test-type-1", "test-type-2"],
            status="active"
        )

        result = self.usecase.execute(new_subscription_request)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "Test Subscription")
        self.assertEqual(result.status, "active")
        self.assertEqual(len(result.resource_types), 2)

    def test_invalid_resource_type(self):
        new_subscription_request = interfaces.requests.NewSubscriptionRequest(
            name="Test Subscription",
            resource_type_ids=["invalid-type"],
            status="active"
        )

        result = self.usecase.execute(new_subscription_request)
        self.assertFalse(result)

    def test_inactive_status(self):
        new_subscription_request = interfaces.requests.NewSubscriptionRequest(
            name="Test Subscription",
            resource_type_ids=["test-type-1"],
            status="inactive"
        )

        result = self.usecase.execute(new_subscription_request)
        self.assertEqual(result.status, "inactive")

    def test_empty_resource_types(self):
        new_subscription_request = interfaces.requests.NewSubscriptionRequest(
            name="Test Subscription",
            resource_type_ids=[],
            status="active"
        )

        result = self.usecase.execute(new_subscription_request)
        self.assertEqual(len(result.resource_types), 0)
