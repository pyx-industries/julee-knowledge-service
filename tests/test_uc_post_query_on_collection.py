import unittest
from uuid import UUID
from datetime import datetime

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockSearchRepository,
    MockCollectionRepository
)

class TestPostQueryOnCollection(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.search_repo = MockSearchRepository()
        self.collection_repo = MockCollectionRepository()

        # Create test collection
        self.test_collection = domain.Collection(
            id="test-collection-1",
            name="Test Collection",
            subscription_id=UUID("00000000-0000-0000-0000-000000000000"),
            resource_types=[domain.ResourceType(
                id="test-type",
                name="Test Type",
                tooltip="Test tooltip")],
            description="Test Description"
        )
        self.collection_repo.collections[self.test_collection.id] = self.test_collection

        # Initialize usecase
        self.usecase = usecases.PostQueryOnCollecton({
            "search_repository": self.search_repo,
            "collection_repository": self.collection_repo
        })

    def test_successful_query_submission(self):
        result = self.usecase.execute({
            "collection_id": self.test_collection.id,
            "query": "test query",
            "filters": {}
        })
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        # Extract search ID from the URL
        self.assertIn('/search/', result.search_url)

    def test_collection_not_found(self):
        with self.assertRaises(Exception):
            self.usecase.execute({
                "collection_id": "non-existent-id",
                "query": "test query",
                "filters": {}
            })

    def test_invalid_query(self):
        with self.assertRaises(ValueError):
            self.usecase.execute({
                "collection_id": self.test_collection.id,
                "query": "",  # Empty query
                "filters": {}
            })

    def test_with_filters(self):
        result = self.usecase.execute({
            "collection_id": self.test_collection.id,
            "query": "test query",
            "filters": {"date_range": "last_week"}
        })
        self.assertTrue(result.success)
        # Extract search ID from URL
        search_id = result.search_url.split('/')[-1]
        saved_request = self.search_repo.get_search_request(search_id)
        self.assertEqual(saved_request.filters["date_range"], "last_week")
