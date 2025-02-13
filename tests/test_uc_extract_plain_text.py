import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockTaskDispatchRepository,
    MockResourceRepository,
    MockFileManagerRepository
)

class TestExtractPlainTextOfResource(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.dispatch_repo = MockTaskDispatchRepository()
        self.resource_repo = MockResourceRepository()
        self.file_manager = MockFileManagerRepository()

        # Create test resource
        self.test_resource = domain.Resource(
            id="test-resource-1",
            collection_id="test-collection",
            resource_type_id="test-type",
            name="Test Resource",
            file_name="test.txt",
            file=b"Test content",
            file_type="text/plain",
            markdown_content=None,
            metadata_file=None,
            callback_urls=[]
        )
        self.resource_repo.resources[self.test_resource.id] = self.test_resource

        # Initialize usecase
        self.usecase = usecases.ExtractPlainTextOfResource({
            "task_dispatch_repository": self.dispatch_repo,
            "resource_repository": self.resource_repo,
            "file_manager_repository": self.file_manager
        })

    def test_successful_text_extraction(self):
        # Execute usecase
        result = self.usecase.execute(self.test_resource.id)

        # Verify interactions
        self.assertIsNone(result)
        self.assertIsNotNone(
            self.resource_repo.get_resource_by_id(self.test_resource.id).markdown_content
        )
        # Verify next task was dispatched
        self.assertEqual(len(self.dispatch_repo.notifications), 1)

    def test_resource_not_found(self):
        with self.assertRaises(Exception) as context:
            self.usecase.execute("non-existent-id")
        self.assertTrue("not found" in str(context.exception))

    def test_already_processed(self):
        # Modify resource to have existing markdown content
        processed_resource = self.test_resource
        processed_resource.markdown_content = "Existing content"
        self.resource_repo.resources[processed_resource.id] = processed_resource

        # Should skip processing but dispatch next task
        result = self.usecase.execute(processed_resource.id)

        self.assertIsNone(result)
        self.assertEqual(len(self.dispatch_repo.notifications), 1)

    def test_missing_file_type(self):
        # Modify resource to have no file type
        bad_resource = self.test_resource
        bad_resource.file_type = None
        self.resource_repo.resources[bad_resource.id] = bad_resource

        with self.assertRaises(Exception) as context:
            self.usecase.execute(bad_resource.id)
        self.assertTrue("File type not determined" in str(context.exception))

    def test_extraction_error(self):
        # Mock extraction error in file manager
        def mock_extract_error(resource):
            raise Exception("Extraction failed")

        self.file_manager.extract_markdown_content = mock_extract_error

        with self.assertRaises(Exception) as context:
            self.usecase.execute(self.test_resource.id)
        self.assertTrue("Failed to extract text" in str(context.exception))
