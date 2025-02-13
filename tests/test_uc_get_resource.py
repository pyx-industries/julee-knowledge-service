import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockResourceRepository
)

class TestGetResource(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.resource_repo = MockResourceRepository()

        # Create test resource
        self.test_resource = domain.Resource( 
            id="00000000-0000-0000-0000-000000000001",
            collection_id="00000000-0000-0000-0000-000000000002",
            resource_type_id="test-type",
            metadata_file=None,
            name="Test Resource",
            file_name="test.txt",
            file=b"Test content",
            file_type="text/plain",
            markdown_content="Test content",
            callback_urls=[]
        )
        self.resource_repo.resources[self.test_resource.id] = self.test_resource

        # Initialize usecase
        self.usecase = usecases.GetResource({
            "resource_repository": self.resource_repo
        })

    def test_successful_get_resource(self):
        result = self.usecase.execute(self.test_resource.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, UUID(self.test_resource.id))
        self.assertEqual(result.name, self.test_resource.name)
        self.assertEqual(result.resource_type_id, self.test_resource.resource_type_id)
        self.assertEqual(result.file_type, self.test_resource.file_type)

    def test_resource_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNone(result)

    def test_resource_without_file(self):
        # Test resource that has been quarantined (file=None)
        quarantined_resource = self.test_resource
        quarantined_resource.file = None
        self.resource_repo.resources[quarantined_resource.id] = quarantined_resource

        result = self.usecase.execute(quarantined_resource.id)
        self.assertIsNotNone(result)
        self.assertIsNone(result.file)

