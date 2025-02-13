import unittest

try:
    from knowledge_service.django_setup import setup_django
except ModuleNotFoundError:
    from django_setup import setup_django


setup_django()


# class TestAPI(unittest.TestCase):
#     def setUp(self):
#         # Set up a test client and resources
#         self.client = TestClient(app)

#         # Set up initial resources
#         self._resource_type_ids = self._get_resource_type_ids()
#         self._subscription_data = requests.NewSubscriptionRequest(
#             name="Test Subscription",
#             resource_type_ids=self._resource_type_ids,
#             status=requests.SubscriptionStatus.active,
#         )
#         # Create a subscription
#         post_response = self.client.post(
#             "/subscriptions/", json=self._subscription_data.model_dump()
#         )
#         self.assertEqual(post_response.status_code, 200)
#         self._subscription_id = post_response.json()["id"]

#         # Create a collection under the subscription
#         self._new_collection_data = requests.NewCollectionRequest(
#             resource_type_ids=self._resource_type_ids,
#             name="Test Collection",
#             description="A test collection",
#         )
#         collection_response = self.client.post(
#             f"/subscriptions/{self._subscription_id}/collections",
#             json=self._new_collection_data.model_dump(),
#         )
#         self.assertEqual(collection_response.status_code, 200)
#         self._collection_id = collection_response.json()["id"]

#     def tearDown(self):
#         # Clean up created resources after each test
#         if hasattr(self, "_collection_id"):
#             self.client.delete(f"/collections/{self._collection_id}")
#         if hasattr(self, "_subscription_id"):
#             self.client.delete(f"/subscriptions/{self._subscription_id}")

#     def _get_resource_type_ids(self):
#         # Helper method to get resource type IDs for the test
#         response = self.client.get("/resource-types/")

#         raise Exception(f"DEBUG: {response.json()}")

#         return [rt["id"] for rt in response.json()["resource_types"]]

#     def test_post_new_subscription(self):
#         # Test the creation of a subscription without resource_types
#         subscription_data = requests.NewSubscriptionRequest(
#             name="Test Subscription 1",
#             resource_type_ids=[],
#             status=requests.SubscriptionStatus.active,
#         )
#         response = self.client.post(
#             "/subscriptions/", json=subscription_data.model_dump()
#         )
#         self.assertEqual(response.status_code, 200)
#         response_data = responses.SubscriptionResponse(**response.json())
#         self.assertEqual(response_data.name, subscription_data.name)
#         self.assertEqual(response_data.status, subscription_data.status)
#         self.assertEqual(len(response_data.resource_types), 0)
#         # Cleanup subscription
#         self.client.delete(f"/subscriptions/{response_data.id}")

#         # Now with resource-types
#         rt_ids = self._get_resource_type_ids()
#         subscription_data = requests.NewSubscriptionRequest(
#             name="Test Subscription 2",
#             resource_type_ids=rt_ids,
#             status=requests.SubscriptionStatus.active,
#         )
#         response = self.client.post(
#             "/subscriptions/", json=subscription_data.model_dump()
#         )
#         self.assertEqual(response.status_code, 200)
#         response_data = responses.SubscriptionResponse(**response.json())
#         self.assertEqual(response_data.name, subscription_data.name)
#         self.assertEqual(response_data.status, subscription_data.status)
#         self.assertEqual(len(response_data.resource_types), len(rt_ids))
#         self.client.delete(f"/subscriptions/{response_data.id}")

#     def test_get_subscription_list(self):
#         # Test retrieving the list of subscriptions
#         response = self.client.get("/subscriptions/")
#         self.assertEqual(response.status_code, 200)
#         response_data = responses.SubscriptionListResponse(**response.json())
#         self.assertIsInstance(response_data.subscriptions, list)
#         self.assertGreater(len(response_data.subscriptions), 0)

#     def test_get_subscription_details(self):
#         # Test retrieving subscription details
#         response = self.client.get(f"/subscriptions/{self._subscription_id}")
#         self.assertEqual(response.status_code, 200)
#         response_data = responses.SubscriptionResponse(**response.json())
#         self.assertEqual(response_data.id, self._subscription_id)

#     def test_get_subscription_not_found(self):
#         # Test for a subscription not found error
#         subscription_id = uuid4()  # Generate a new fake UUID
#         response = self.client.get(f"/subscriptions/{subscription_id}")
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(
#             response.json()["detail"],
#             f"Subscription with ID {subscription_id} not found",
#         )

#     def test_post_new_collection_to_subscription(self):
#         # Test creating a new collection under an existing subscription
#         new_collection = requests.NewCollectionRequest(
#             resource_type_ids=self._resource_type_ids,
#             name="Test New Collection",
#             description="A test collection that I'm creating to see if i can",
#         )
#         response = self.client.post(
#             f"/subscriptions/{self._subscription_id}/collections",
#             json=new_collection.model_dump(),
#         )
#         self.assertEqual(response.status_code, 200)
#         response_data = responses.CollectionResponse(**response.json())
#         self.assertEqual(response_data.name, new_collection.name)
#         self.assertEqual(response_data.num_resources, 0)
#         # Cleanup collection
#         self.client.delete(f"/collections/{response_data.id}")

#     def test_post_new_collection_conflict(self):
#         # Test creating a collection that already exists (conflict)
#         new_collection = requests.NewCollectionRequest(
#             resource_type_ids=self._resource_type_ids,
#             name="Duplication Test Collection",
#             description="A test collection, twice attempt created",
#         )
#         response = self.client.post(
#             f"/subscriptions/{self._subscription_id}/collections",
#             json=new_collection.model_dump(),
#         )
#         self.assertEqual(response.status_code, 200)
#         collection_id = response.json()["id"]
#         # Try creating the same collection again (should cause a conflict)
#         response = self.client.post(
#             f"/subscriptions/{self._subscription_id}/collections",
#             json=new_collection.model_dump(),
#         )
#         self.assertEqual(response.status_code, 409)
#         self.assertIn("already exists", response.json()["detail"])
#         # Cleanup
#         self.client.delete(f"/collections/{collection_id}")

#     def test_delete_subscription(self):
#         # Test deleting a subscription
#         response = self.client.delete(
#             f"/subscriptions/{self._subscription_id}"
#         )
#         self.assertEqual(response.status_code, 200)
#         response_data = responses.DeleteSubscriptionResponse(
#             **response.json()
#         )
#         self.assertTrue(response_data.success)
#         self.assertIsInstance(response_data.timestamp, str)

#     def test_delete_subscription_not_found(self):
#         # Test deleting a non-existent subscription
#         subscription_id = uuid4()  # Generate a new fake UUID
#         response = self.client.delete(f"/subscriptions/{subscription_id}")
#         self.assertEqual(response.status_code, 404)
#         self.assertIn("Subscription not found", response.json()["message"])

#     def test_get_collection_details(self):
#         # Test retrieving collection details
#         response = self.client.get(f"/collections/{self._collection_id}")
#         self.assertEqual(response.status_code, 200)
#         response_data = responses.CollectionResponse(**response.json())
#         self.assertEqual(response_data.id, self._collection_id)

#     def test_get_resource_list(self):
#         # Test retrieving the list of resources in a collection
#         response = self.client.get(
#             f"/collections/{self._collection_id}/resources"
#         )
#         self.assertEqual(response.status_code, 200)
#         response_data = responses.ResourceListResponse(**response.json())
#         self.assertIsInstance(response_data.resources, list)

#     def test_post_new_resource_to_collection(self):
#         # Test uploading a new resource to a collection
#         resource_data = requests.ResourceUploadRequest(
#             file_name="test.txt",
#             file_content=b"Test data",
#             name="delete this file",
#             collection_id=str(self._collection_id),
#             resource_type_id=str(self._resource_type_ids[0]),
#             webhooks=["http://example.com/webhook"],
#             metadata=json.dumps({"key": "value"}),
#         )
#         file_data = io.BytesIO(b"Test data")
#         file_data.name = "test.txt"
#         response = self.client.post(
#             f"/collections/{self._collection_id}/{self._resource_type_ids[0]}",
#             files={"new_resource": ("test.txt", file_data, "text/plain")},
#             data={
#                 "file_name": resource_data.file_name,
#                 "name": resource_data.name,
#                 "webhooks": [
#                     "http://localhost/callback",
#                 ],
#             },
#         )
#         try:
#             self.assertEqual(response.status_code, 200)
#         except AssertionError:
#             print(f"DEBUG: name = {resource_data.name}")
#             print(f"DEBUG: {response.json()}")
#             self.assertEqual(response.status_code, 200)
#         response_data = responses.ResourceUploadResponse(**response.json())
#         self.assertEqual(response_data.success, True)
#         self.assertIsNotNone(response_data.resource_url)
#         # Cleanup
#         self.client.delete(f"/resources/{response_data.resource_id}")

#     def test_delete_collection(self):
#         # Test deleting a collection
#         response = self.client.delete(f"/collections/{self._collection_id}")
#         self.assertEqual(response.status_code, 200)
#         response_data = responses.DeleteCollectionResponse(**response.json())
#         self.assertTrue(response_data.success)
#         self.assertIsInstance(response_data.timestamp, datetime)


if __name__ == "__main__":
    unittest.main()
