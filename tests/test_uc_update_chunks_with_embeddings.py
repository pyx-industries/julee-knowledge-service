import unittest
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockTaskDispatchRepository,
    MockGraphRepository,
    MockLanguageModelRepository
)

class TestUpdateChunksWithEmbeddings(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.dispatch_repo = MockTaskDispatchRepository()
        self.graph_repo = MockGraphRepository()
        self.language_model_repo = MockLanguageModelRepository()

        # Create test chunks
        self.test_chunks = [
            domain.ResourceChunk(
                id="chunk-1",
                resource_id="test-resource-1",
                text="Test chunk 1",
                sequence=0,
                extract="Test chunk 1",
                metadata={"position": 0}
            ),
            domain.ResourceChunk(
                id="chunk-2", 
                resource_id="test-resource-1",
                text="Test chunk 2",
                sequence=1,
                extract="Test chunk 2",
                metadata={"position": 1}
            )
        ]

        # Initialize usecase
        self.usecase = usecases.UpdateChunksWithEmbeddings({
            "task_dispatch_repository": self.dispatch_repo,
            "graph_repository": self.graph_repo,
            "language_model_repository": self.language_model_repo
        })

    def test_successful_embedding_update(self):
        # Mock chunks without embeddings
        self.graph_repo.get_chunks_without_embeddings = lambda x: self.test_chunks

        # Execute usecase
        result = self.usecase.execute("test-resource-1")

        # Verify interactions
        self.assertIsNone(result)
        # Verify embeddings were generated and stored
        self.assertEqual(len(self.language_model_repo.embeddings), 2)
        # Verify next task was dispatched
        self.assertEqual(len(self.dispatch_repo.notifications), 1)

    def test_no_chunks_without_embeddings(self):
        # Mock no chunks needing embeddings
        self.graph_repo.get_chunks_without_embeddings = lambda x: []

        result = self.usecase.execute("test-resource-1")
        self.assertTrue(result)
        self.assertEqual(len(self.dispatch_repo.notifications), 0)

    def test_embedding_generation_error(self):
        # Mock chunks without embeddings
        self.graph_repo.get_chunks_without_embeddings = lambda x: self.test_chunks

        # Mock embedding error
        def mock_embedding_error(text):
            raise Exception("Embedding generation failed")

        self.language_model_repo.generate_embedding = mock_embedding_error

        with self.assertRaises(Exception) as context:
            self.usecase.execute("test-resource-1")

    def test_graph_update_error(self):
        # Mock chunks without embeddings
        self.graph_repo.get_chunks_without_embeddings = lambda x: self.test_chunks

        # Mock graph update error
        def mock_update_error(chunk, embedding):
            raise Exception("Graph update failed")

        self.graph_repo.update_chunk_embedding = mock_update_error

        with self.assertRaises(Exception) as context:
            self.usecase.execute("test-resource-1")
