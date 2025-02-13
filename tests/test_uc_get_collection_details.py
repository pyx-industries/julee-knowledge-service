import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import ( 
    MockCollectionRepository, 
    MockResourceRepository 
) 

class TestGetCollectionDetails(unittest.TestCase):
    def setUp(self): 
        # Initialize mock repositories 
        self.collection_repo = MockCollectionRepository() 
        self.resource_repo = MockResourceRepository()

        # Create test collection 
        self.test_collection = domain.Collection( 
            id="00000000-0000-0000-0000-000000000001", 
            name="Test Collection", 
            subscription_id=UUID("00000000-0000-0000-0000-000000000000"), 
            resource_types=[ 
                domain.ResourceType( 
                    id="test-type", 
                    name="Test Type", 
                    tooltip="A test resource type" 
                )], 
            description="Test Description" 
        ) 
        self.collection_repo.collections[self.test_collection.id] = self.test_collection 

        # Initialize usecase 
        self.usecase = usecases.GetCollectionDetails({ 
            "collection_repository": self.collection_repo, 
            "resource_repository": self.resource_repo 
        }) 

    def test_successful_get_details(self):
        result = self.usecase.execute(self.test_collection.id)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, str(self.test_collection.id))
        self.assertEqual(result.name, self.test_collection.name)

    def test_collection_not_found(self):
        non_existent_id = "non-existent-id"
        result = self.usecase.execute(non_existent_id)
        self.assertIsNone(result)

    def test_with_resources(self):
        # TODO: Add test for collection with resources once resource count is implemented
        result = self.usecase.execute(self.test_collection.id)
        self.assertEqual(result.num_resources, 0)
