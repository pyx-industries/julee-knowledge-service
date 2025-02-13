import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockResourceRepository
)

class TestGetResourceList(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.resource_repo = MockResourceRepository()

        # Create test resources
        self.test_resources = [
            domain.Resource(
                id="test-resource-1",
                collection_id="test-collection",
                resource_type_id="test-type",
                name="Test Resource 1",
                file_name="test1.txt",
                file=b"Test content 1",
                file_type="text/plain",
                markdown_content=None,
                metadata_file=None,
                callback_urls=[]
            ),
            domain.Resource(
                id="test-resource-2", 
                collection_id="test-collection",
                resource_type_id="test-type",
                name="Test Resource 2",
                file_name="test2.txt",
                file=b"Test content 2",
                file_type="text/plain",
                markdown_content=None,
                metadata_file=None,
                callback_urls=[]
            )
        ]

        for resource in self.test_resources:
            self.resource_repo.resources[resource.id] = resource

        # Initialize usecase
        self.usecase = usecases.GetResourceList({
            "resource_repository": self.resource_repo
        })

    def test_get_all_resources(self):
        result = self.usecase.execute("test-collection")
        self.assertIsNotNone(result)
        self.assertEqual(len(result.resources), 2)
        self.assertEqual(result.resources[0].name, "Test Resource 1")
        self.assertEqual(result.resources[1].name, "Test Resource 2")

    def test_empty_collection(self):
        # Clear resources
        self.resource_repo.resources.clear()

        result = self.usecase.execute("test-collection")
        self.assertEqual(len(result.resources), 0)

    def test_filter_by_collection(self):
        # Add resource from different collection
        other_resource = domain.Resource(
            id="test-resource-3",
            collection_id="other-collection",
            resource_type_id="test-type",
            name="Other Resource",
            file_name="other.txt",
            file=b"Other content",
            file_type="text/plain",
            markdown_content=None,
            metadata_file=None,
            callback_urls=[]
        )
        self.resource_repo.resources[other_resource.id] = other_resource

        result = self.usecase.execute("test-collection")
        self.assertEqual(len(result.resources), 2)
        for resource in result.resources:
            self.assertEqual(resource.collection_id, "test-collection")
