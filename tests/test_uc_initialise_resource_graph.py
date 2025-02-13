import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockTaskDispatchRepository,
    MockResourceRepository,
    MockGraphRepository,
    MockCollectionRepository,
    MockSubscriptionRepository
)

class TestInitialiseResourceGraph(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.dispatch_repo = MockTaskDispatchRepository()
        self.resource_repo = MockResourceRepository()
        self.graph_repo = MockGraphRepository()
        self.collection_repo = MockCollectionRepository()
        self.subscription_repo = MockSubscriptionRepository()

        # Create test data
        self.test_resource = domain.Resource(
            id="test-resource-1",
            collection_id="test-collection",
            resource_type_id="test-type",
            name="Test Resource",
            file_name="test.txt",
            file=b"Test content",
            file_type="text/plain",
            markdown_content=None,
            callback_urls=[],
            metadata_file={}
        )
        self.resource_repo.resources[self.test_resource.id] = self.test_resource

        self.test_collection = domain.Collection(
            id="test-collection",
            name="Test Collection",
            subscription_id=UUID("00000000-0000-0000-0000-000000000000"),
            resource_types=["test-type"],
            description=""
        )
        self.collection_repo.collections[self.test_collection.id] = self.test_collection

        self.test_subscription = domain.Subscription(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            name="Test Subscription",
            resource_types=["test-type"],
            is_active=True,
            collections=[]
        )
        self.subscription_repo.subscriptions[self.test_subscription.id] = self.test_subscription

        # Initialize usecase
        self.usecase = usecases.InitialiseResourceGraph({
            "task_dispatch_repository": self.dispatch_repo,
            "resource_repository": self.resource_repo,
            "graph_repository": self.graph_repo,
            "collection_repository": self.collection_repo,
            "subscription_repository": self.subscription_repo
        })

    def test_successful_graph_initialization(self):
        # Execute usecase
        result = self.usecase.execute(self.test_resource.id)

        # Verify interactions
        self.assertIsNone(result)
        self.assertTrue(
            self.graph_repo.check_resource_node_exists(self.test_resource.id)
        )
        # Verify next task was dispatched
        self.assertEqual(len(self.dispatch_repo.notifications), 1)

    def test_resource_not_found(self):
        with self.assertRaises(Exception) as context:
            self.usecase.execute("non-existent-id")
        self.assertTrue("not found" in str(context.exception))

    def test_collection_not_found(self):
        bad_resource = self.test_resource
        bad_resource.collection_id = "non-existent-collection"
        self.resource_repo.resources[bad_resource.id] = bad_resource

        with self.assertRaises(Exception) as context:
            self.usecase.execute(bad_resource.id)
        self.assertTrue("collection not found" in str(context.exception))

    def test_subscription_not_found(self):
        bad_collection = self.test_collection
        bad_collection.subscription_id = UUID("11111111-1111-1111-1111-111111111111")
        self.collection_repo.collections[bad_collection.id] = bad_collection

        with self.assertRaises(Exception) as context:
            self.usecase.execute(self.test_resource.id)
        self.assertTrue("subscription not found" in str(context.exception))

    def test_empty_file(self):
        empty_resource = self.test_resource
        empty_resource.file = b""
        self.resource_repo.resources[empty_resource.id] = empty_resource

        with self.assertRaises(AssertionError):
            self.usecase.execute(empty_resource.id)
