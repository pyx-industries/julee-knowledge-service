import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.repositories import FileAnalysisResult
from knowledge_service.tests.mock_repos import (
    MockFileManagerRepository,
    MockVirusQuarantineRepository,
    MockTaskDispatchRepository,
    MockResourceRepository
)

class TestInitiateProcessingOfNewResource(unittest.TestCase):
    """Test suite for InitiateProcessingOfNewResource usecase.

    Tests the initial validation and safety checks performed on newly uploaded resources:
    - Successful processing initiation
    - Virus detection and quarantine
    - Resource not found handling
    - Empty file validation
    """
    def setUp(self):
        # Initialize mock repositories
        self.file_manager = MockFileManagerRepository()
        self.virus_quarantine = MockVirusQuarantineRepository()
        self.task_dispatch = MockTaskDispatchRepository()
        self.resource_repo = MockResourceRepository()

        # Create test resource
        self.test_resource = domain.Resource(
            id="test-resource-1",
            collection_id="test-collection",
            resource_type_id="test-type",
            name="Test Resource",
            file_name="test.txt",
            file=b"Test content",
            file_type=None,
            markdown_content=None,
            callback_urls=[],
            metadata_file={}
        )
        self.resource_repo.resources[self.test_resource.id] = self.test_resource

        # Initialize usecase with mock repos
        self.usecase = usecases.InitiateProcessingOfNewResource({
            "file_manager_repository": self.file_manager,
            "virus_quarantine_repository": self.virus_quarantine,
            "task_dispatch_repository": self.task_dispatch,
            "resource_repository": self.resource_repo
        })

    def test_successful_processing_initiation(self):
        """When a valid resource is processed,
        then:
        - File type should be detected as text/plain
        - Resource should be updated with detected type
        - Processing should be initiated without errors
        - No exceptions should be raised
        """
        # Execute usecase
        result = self.usecase.execute(self.test_resource.id)

        # Verify interactions
        self.assertIsNone(result)
        self.assertEqual(self.file_manager.detect_file_type(self.test_resource), "text/plain")
        self.assertEqual(
            self.resource_repo.get_resource_by_id(self.test_resource.id).file_type,
            "text/plain"
        )

    def test_virus_detected(self):
        """When a resource containing a virus is processed,
        then:
        - Resource should be quarantined
        - Original file content should be cleared
        - Exception should be raised with 'failed virus scan' message
        - Further processing should be halted
        """
        # Modify test resource to contain virus
        infected_resource = self.test_resource
        infected_resource.file = b"VIRUS content"
        self.resource_repo.resources[infected_resource.id] = infected_resource

        # Execute usecase and verify exception
        with self.assertRaises(Exception) as context:
            self.usecase.execute(infected_resource.id)

        self.assertTrue("failed virus scan" in str(context.exception))
        self.assertTrue(self.virus_quarantine.is_quarantined(infected_resource.id))
        self.assertIsNone(
            self.resource_repo.get_resource_by_id(infected_resource.id).file
        )

    def test_resource_not_found(self):
        """When a non-existent resource ID is processed,
        then an exception should be raised with 'not found' in the message
        """
        with self.assertRaises(Exception) as context:
            self.usecase.execute("non-existent-id")
        self.assertTrue("not found" in str(context.exception))

    def test_empty_file(self):
        """When a resource with empty file content is processed,
        then an AssertionError should be raised due to empty content validation
        """
        empty_resource = self.test_resource
        empty_resource.file = b""
        self.resource_repo.resources[empty_resource.id] = empty_resource

        with self.assertRaises(AssertionError):
            self.usecase.execute(empty_resource.id)
