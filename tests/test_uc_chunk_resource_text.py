import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockTaskDispatchRepository,
    MockResourceRepository,
    MockResourceTypeRepository,
    MockGraphRepository,
    MockChunkingRepository
)

class TestChunkResourceText(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.dispatch_repo = MockTaskDispatchRepository()
        self.resource_repo = MockResourceRepository()
        self.resource_type_repo = MockResourceTypeRepository()
        self.graph_repo = MockGraphRepository()
        self.chunking_repo = MockChunkingRepository()

        # Create test resource
        self.test_resource = domain.Resource(
            id="test-resource-1",
            collection_id="test-collection",
            resource_type_id="test-type",
            name="Test Resource",
            file_name="test.txt",
            file=b"Test content",
            file_type="text/plain",
            markdown_content="Test paragraph 1\n\nTest paragraph 2",
            metadata_file=None,
            callback_urls=[]
        )
        self.resource_repo.resources[self.test_resource.id] = self.test_resource

        # Create test resource type
        self.test_resource_type = domain.ResourceType(
            id="test-type",
            name="Test Type",
            tooltip="Test tooltip"
        )
        self.resource_type_repo.resource_types[self.test_resource_type.id] = self.test_resource_type

        # Initialize usecase
        self.usecase = usecases.ChunkResourceText({
            "task_dispatch_repository": self.dispatch_repo,
            "resource_repository": self.resource_repo,
            "resource_type_repository": self.resource_type_repo,
            "graph_repository": self.graph_repo,
            "chunking_repository": self.chunking_repo
        })

    def test_successful_chunking(self):
        result = self.usecase.execute(self.test_resource.id)
        self.assertIsNone(result)
        # Verify chunks were created in graph
        self.assertTrue(len(self.graph_repo.nodes) > 0)
        # Verify next task was dispatched
        self.assertEqual(len(self.dispatch_repo.notifications), 1)

    def test_resource_not_found(self):
        with self.assertRaises(Exception) as context:
            self.usecase.execute("non-existent-id")
        self.assertTrue("not found" in str(context.exception))

    def test_no_markdown_content(self):
        resource_no_markdown = self.test_resource
        resource_no_markdown.markdown_content = None
        self.resource_repo.resources[resource_no_markdown.id] = resource_no_markdown

        with self.assertRaises(Exception) as context:
            self.usecase.execute(resource_no_markdown.id)
        self.assertTrue("no markdown content" in str(context.exception).lower())

    def test_resource_type_not_found(self):
        resource_bad_type = self.test_resource
        resource_bad_type.resource_type_id = "non-existent-type"
        self.resource_repo.resources[resource_bad_type.id] = resource_bad_type

        with self.assertRaises(Exception) as context:
            self.usecase.execute(resource_bad_type.id)
        self.assertTrue("type not found" in str(context.exception).lower())

    def test_chunking_error(self):
        def mock_chunking_error(*args):
            raise Exception("Chunking failed")

        self.chunking_repo.chunk_resource = mock_chunking_error

        with self.assertRaises(Exception) as context:
            self.usecase.execute(self.test_resource.id)
        error_msg = str(context.exception).lower()
        self.assertTrue(
            "failed to create chunks" in error_msg or 
            "chunking failed" in error_msg
        )
