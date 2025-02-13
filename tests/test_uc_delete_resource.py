import unittest
from uuid import UUID
from datetime import datetime

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockResourceRepository,
    MockGraphRepository
)

class TestMockGraphRepository(MockGraphRepository):
    def soft_delete(self, resource_id: str):
        if resource_id not in self.nodes:
            raise Exception("Resource not found in graph")
        self.nodes[resource_id].is_deleted = True

class TestDeleteResource(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.resource_repo = MockResourceRepository()
        self.graph_repo = TestMockGraphRepository()

        # Create test resource
        self.test_resource = domain.Resource(
            id="test-resource-1",
            collection_id="test-collection",
            resource_type_id="test-type",
            name="Test Resource",
            file_name="test.txt",
            file=b"Test content",
            file_type="text/plain",
            markdown_content="Test content",
            metadata_file=None,
            callback_urls=[]
        )
        self.resource_repo.resources[self.test_resource.id] = self.test_resource
        self.graph_repo.nodes[self.test_resource.id] = self.test_resource

        # Initialize usecase
        self.usecase = usecases.DeleteResource({
            "resource_repository": self.resource_repo,
            "graph_repository": self.graph_repo
        })

    def test_successful_deletion(self):
        print("\nTEST: Starting deletion test")
        print(f"TEST: Resource exists in repo before? {self.test_resource.id in self.resource_repo.resources}")
        print(f"TEST: Resource exists in graph before? {self.test_resource.id in self.graph_repo.nodes}")
        
        result = self.usecase.execute(self.test_resource.id)
        print(f"TEST: Got result with success={result.success}, message={result.message}")
        
        print(f"TEST: Resource exists in repo after? {self.test_resource.id in self.resource_repo.resources}")
        print(f"TEST: Resource exists in graph after? {self.test_resource.id in self.graph_repo.nodes}")
        if self.test_resource.id in self.graph_repo.nodes:
            print(f"TEST: Resource deleted in graph? {getattr(self.graph_repo.nodes[self.test_resource.id], 'is_deleted', False)}")
        
        self.assertTrue(result.success)
        self.assertEqual(result.id, self.test_resource.id)
        self.assertIsInstance(result.timestamp, datetime)
        
        # Verify resource was deleted from repository
        self.assertNotIn(self.test_resource.id, self.resource_repo.resources)
        
        # Verify soft delete in graph
        self.assertIn(self.test_resource.id, self.graph_repo.nodes)
        self.assertTrue(self.graph_repo.nodes[self.test_resource.id].is_deleted)

    def test_resource_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertFalse(result.success)
        self.assertEqual(result.id, "non-existent-id")
        self.assertIn("not found", result.message.lower())

    def test_already_deleted(self):
        # Delete once
        self.usecase.execute(self.test_resource.id)
        # Try to delete again
        result = self.usecase.execute(self.test_resource.id)
        self.assertFalse(result.success)
        self.assertIn("already deleted", result.message.lower())

    def test_graph_error_handling(self):
        # Mock graph error
        def mock_graph_error(resource_id):
            raise Exception("Graph error")
            
        self.graph_repo.soft_delete = mock_graph_error

        result = self.usecase.execute(self.test_resource.id)
        self.assertFalse(result.success)
        self.assertIn("graph error", result.message.lower())
        # Verify resource not deleted from repository on graph error
        self.assertIn(self.test_resource.id, self.resource_repo.resources)
