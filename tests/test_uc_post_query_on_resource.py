import unittest
from uuid import UUID
from datetime import datetime

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSearchRepository,
    MockResourceRepository
)

class TestPostQueryOnResource(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.search_repo = MockSearchRepository()
        self.resource_repo = MockResourceRepository()

        # Create test resource
        self.test_resource = domain.Resource(
            id="test-resource-1",
            collection_id="test-collection",
            resource_type_id="test-type",
            name="Test Resource",
            file_name="test.txt",
            file=b"Test content",
            metadata_file={},
            file_type="text/plain",
            markdown_content="Test content",
            callback_urls=[]
        )
        self.resource_repo.resources[self.test_resource.id] = self.test_resource

        # Initialize usecase
        self.usecase = usecases.PostQueryOnResource({
            "search_repository": self.search_repo,
            "resource_repository": self.resource_repo
        })

    def test_successful_query_submission(self):
        result = self.usecase.execute({
            "resource_id": self.test_resource.id,
            "query": "test query",
            "filters": {}
        })
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        # Extract search ID from the URL
        self.assertIn('/search/', result.search_url)

    def test_resource_not_found(self):
        with self.assertRaises(Exception):
            self.usecase.execute({
                "resource_id": "non-existent-id",
                "query": "test query",
                "filters": {}
            })

    def test_invalid_query(self):
        with self.assertRaises(ValueError):
            self.usecase.execute({
                "resource_id": self.test_resource.id,
                "query": "",  # Empty query
                "filters": {}
            })

    def test_with_callback_urls(self):
        result = self.usecase.execute({
            "resource_id": self.test_resource.id,
            "query": "test query",
            "filters": {},
            "callback_urls": ["http://test.com/callback"]
        })
        self.assertTrue(result.success)
        search_id = result.search_url.split('/')[-1]
        saved_request = self.search_repo.get_search_request(search_id)
        self.assertIn("http://test.com/callback", saved_request.callback_urls)
