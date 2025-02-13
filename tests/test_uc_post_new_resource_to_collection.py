import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.interfaces import requests, responses
from knowledge_service.tests.mock_repos import (
    MockCollectionRepository,
    MockResourceRepository,
    MockResourceTypeRepository,
    MockTaskDispatchRepository
)

class TestPostNewResourceToCollection(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures:
        - Mock repositories
        - Test resource type
        - Test collection with allowed resource type
        - Initialize use case with mocks
        """
        # Initialize repositories
        self.collection_repo = MockCollectionRepository()
        self.resource_repo = MockResourceRepository()
        self.resource_type_repo = MockResourceTypeRepository()
        self.task_dispatch_repo = MockTaskDispatchRepository()

        # Create test resource types
        self.test_resource_type = domain.ResourceType( 
            id="test-type-1",
            name="Test Type 1",
            tooltip="Test tooltip 1"
        )
        self.resource_type_repo.resource_types[self.test_resource_type.id] = self.test_resource_type

        # Create test collection
        self.test_collection = domain.Collection(
            id=str(UUID("00000000-0000-0000-0000-000000000000")),
            name="Test Collection", 
            subscription_id=str(UUID("00000000-0000-0000-0000-000000000001")),
            resource_types=[self.test_resource_type],
            description="Test collection description" 
        )
        self.collection_repo.collections[self.test_collection.id] = self.test_collection

        # Initialize use case
        self.usecase = usecases.PostNewResourceToCollection({
            "collection_repository": self.collection_repo,
            "resource_repository": self.resource_repo,
            "resource_type_repository": self.resource_type_repo,
            "task_dispatch_repository": self.task_dispatch_repo
        })

    """Test suite for PostNewResourceToCollection use case.

    Tests the validation and creation of new resources:
    - Successful upload with valid data
    - Invalid collection handling
    - Invalid resource type handling
    - Resource type not allowed for collection
    """

    def test_successful_resource_upload(self):
        """Test successful resource upload flow:


        Given:

        - Valid collection ID
        - Allowed resource type
        - Complete resource metadata and content

        Then:

        - Resource should be created in repository
        - Resource should have correct metadata
        - Processing should be initiated
        - Success response with resource ID returned
        - Webhooks should be preserved
        """
        request = requests.ResourceUploadRequest(
            collection_id=self.test_collection.id,
            resource_type_id=self.test_resource_type.id,
            name="Test Resource",
            file_name="test.txt",
            file_content=b"Test content",
            webhooks=["http://test.com/callback"]
        )

        # Execute use case
        result = self.usecase.execute(request)

        # Verify response
        self.assertIsInstance(result, responses.ResourceUploadResponse)
        self.assertEqual(result.status, responses.ProcessingStatus.pending)
        self.assertIsNotNone(result.resource_id)
        self.assertEqual(result.webhooks, ["http://test.com/callback"])

        # Verify resource was created
        created_resource = self.resource_repo.get_resource_by_id(result.resource_id)
        self.assertIsNotNone(created_resource)
        self.assertEqual(created_resource.name, "Test Resource")
        self.assertEqual(created_resource.collection_id, self.test_collection.id)

    def test_invalid_collection_id(self):
        """Test handling of invalid collection ID:


        Given:

        - Non-existent collection ID
        - Otherwise valid request

        Then:

        - Should raise ValueError
        - Error message should mention 'Collection'
        """
        request = requests.ResourceUploadRequest(
            collection_id="invalid-id",
            resource_type_id=self.test_resource_type.id,
            name="Test Resource",
            file_name="test.txt",
            file_content=b"Test content"
        )

        with self.assertRaises(ValueError) as context:
            self.usecase.execute(request)
        self.assertIn("Collection", str(context.exception))

    def test_invalid_resource_type(self):
        """Test handling of invalid resource type:


        Given:

        - Valid collection ID
        - Non-existent resource type ID

        Then:

        - Should raise ValueError
        - Error message should mention 'Resource type'
        """
        request = requests.ResourceUploadRequest(
            collection_id=self.test_collection.id,
            resource_type_id="invalid-type",
            name="Test Resource",
            file_name="test.txt",
            file_content=b"Test content"
        )

        with self.assertRaises(ValueError) as context:
            self.usecase.execute(request)
        self.assertIn("Resource type", str(context.exception))

    def test_resource_type_not_allowed_for_collection(self):
        """Test handling of disallowed resource type:


        Given:

        - Valid collection ID
        - Valid but unallowed resource type

        Then:

        - Should raise ValueError
        - Error message should mention 'not allowed in collection'
        """
        # Create new resource type not in collection
        new_type = domain.ResourceType(
            id="test-type-2",
            name="Test Type 2",
            tooltip="Test tooltip 2"
        )
        self.resource_type_repo.resource_types[new_type.id] = new_type

        request = requests.ResourceUploadRequest(
            collection_id=self.test_collection.id,
            resource_type_id=new_type.id,
            name="Test Resource",
            file_name="test.txt",
            file_content=b"Test content"
        )

        with self.assertRaises(ValueError) as context:
            self.usecase.execute(request)
        self.assertIn("not allowed in collection", str(context.exception))
