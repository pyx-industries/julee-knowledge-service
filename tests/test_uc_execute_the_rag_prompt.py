import unittest
from datetime import datetime
from uuid import UUID

from knowledge_service import domain, usecases
from knowledge_service.tests.mock_repos import (
    MockGraphRepository,
    MockLanguageModelRepository,
    MockSearchRepository
)

class TestExecuteTheRagPrompt(unittest.TestCase):
    def setUp(self):
        # Initialize mock repositories
        self.graph_repo = MockGraphRepository()
        self.language_model_repo = MockLanguageModelRepository()
        self.search_repo = MockSearchRepository()

        # Create test search request
        self.test_search_request = domain.SearchRequest(
            id="search-1",
            collection_id="test-collection",
            query="test query",
            filters={},
            created_at=datetime.now()
        )
        self.search_repo.search_requests[self.test_search_request.id] = self.test_search_request

        # Create test chunks with high similarity scores
        self.test_chunks = [
            domain.ResourceChunk(
                id="chunk-1",
                resource_id="test-resource-1",
                sequence=1,
                text="Relevant context 1",
                extract="Relevant context 1",
                metadata={"score": 0.9}
            ),
            domain.ResourceChunk(
                id="chunk-2",
                resource_id="test-resource-1",
                sequence=2,
                text="Relevant context 2",
                extract="Relevant context 2",
                metadata={"score": 0.8}
            )
        ]

        # Initialize usecase
        self.usecase = usecases.ExecuteTheRagPrompt({
            "graph_repository": self.graph_repo,
            "language_model_repository": self.language_model_repo,
            "search_repository": self.search_repo
        })

    def test_successful_rag_execution(self):
        # Mock graph repo to return test chunks
        self.graph_repo.get_relevant_chunks = lambda x: self.test_chunks

        result = self.usecase.execute(self.test_search_request.id)
        self.assertIsNotNone(result)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.message)
        self.assertIsNotNone(result.search_url)
        self.assertIsNotNone(result.prompt)
        self.assertEqual(len(result.context_chunks), 2)

    def test_search_request_not_found(self):
        result = self.usecase.execute("non-existent-id")
        self.assertIsNone(result)

    def test_no_relevant_chunks(self):
        # Mock graph repo to return no chunks
        self.graph_repo.get_relevant_chunks = lambda x: []

        result = self.usecase.execute(self.test_search_request.id)
        self.assertFalse(result.success)
        self.assertIn("no relevant context found", result.message.lower())
        self.assertIsNone(result.search_url)

    def test_language_model_error(self):
        # Mock graph repo to return test chunks
        self.graph_repo.get_relevant_chunks = lambda x: self.test_chunks

        # Mock LLM error
        def mock_llm_error(prompt, context):
            raise Exception("LLM generation failed")

        self.language_model_repo.generate_rag_response = mock_llm_error

        result = self.usecase.execute(self.test_search_request.id)
        self.assertFalse(result.success)
        self.assertIn("generation failed", result.message.lower())
        self.assertIsNone(result.search_url)

    def test_prompt_template_rendering(self):
        # Mock graph repo to return test chunks
        self.graph_repo.get_relevant_chunks = lambda x: self.test_chunks

        result = self.usecase.execute(self.test_search_request.id)
        self.assertIsNotNone(result.prompt)
        self.assertIn(self.test_search_request.query, result.prompt)
        self.assertIn("Relevant context 1", result.prompt)
        self.assertIn("Relevant context 2", result.prompt)
