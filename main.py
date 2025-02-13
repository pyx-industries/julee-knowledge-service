import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional
from uuid import UUID

import usecases
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from interfaces import requests, responses

from config import reposet

app = FastAPI(
    title="Pyx Knowledge Service API",
    description="""Example implementation of a service for
    managing and querying collections of semantic resources,
    that provides the Knowledge Service API required by Julee""",
    version="0.0.1",
    docs_url="/",
)
# static content
app.mount(
    "/diagrams",
    StaticFiles(directory=Path(__file__).parent / "diagrams"),
    name="diagrams",
)

uc_get_resource_type_list = usecases.GetResourceTypeList(reposet)
uc_get_subscription_list = usecases.GetSubscriptionList(reposet)
uc_get_subscription_details = usecases.GetSubscriptionDetails(reposet)
uc_get_subscription_resource_type_list = (
    usecases.GetSubscriptionResourceTypeList(reposet)
)
uc_get_subscription_collection_list = usecases.GetSubscriptionCollectionList(
    reposet
)
uc_delete_subscription = usecases.DeleteSubscription(reposet)
uc_post_new_subscription = usecases.PostNewSubscription(reposet)
uc_post_new_collection_to_subscription = (
    usecases.PostNewCollectionToSubscription(reposet)
)
uc_delete_collection = usecases.DeleteCollection(reposet)
uc_get_collection_details = usecases.GetCollectionDetails(reposet)
uc_get_resource_list = usecases.GetResourceList(reposet)
uc_post_new_resource_to_collection = usecases.PostNewResourceToCollection(
    reposet
)

# junky incomplete/untested stuff
uc_get_collection_resource_type_list = usecases.GetCollectionResourceTypeList(
    reposet
)
uc_get_collection_list = usecases.GetCollectionList(reposet)
# uc_get_resource = usecases.GetResource(reposet)
# uc_get_resource_metadata = usecases.GetResourceMetadata(reposet)
uc_post_query_on_collection = usecases.PostQueryOnCollecton(reposet)
uc_post_query_on_resource = usecases.PostQueryOnResource(reposet)
uc_get_query_result = usecases.GetQueryResult(reposet)
uc_get_query_result_metadata = usecases.GetQueryResultMetadata(reposet)
uc_delete_resource = usecases.DeleteResource(reposet)

# so we can run blocking code in a background thread
executor = ThreadPoolExecutor()


# subscriptions
@app.post(
    "/subscriptions/",
    response_model=responses.SubscriptionResponse,
    tags=["Manage Subscriptions"],
)
def post_new_subscription(
    new_subscription: requests.NewSubscriptionRequest,
) -> responses.SubscriptionResponse:
    """Save a new Subscription."""
    return uc_post_new_subscription.execute(new_subscription)


@app.get(
    "/subscriptions/",
    response_model=responses.SubscriptionListResponse,
    tags=["Manage Subscriptions"],
)
def get_subscription_list() -> responses.SubscriptionListResponse:
    """List of subscriptions.

    This is really an admin function,
    it probably shouldn't be exposed.
    For now, it's a just a pragmatic convenience
    until we have an authentication and access control solution.
    """
    return uc_get_subscription_list.execute()


@app.get(
    "/subscriptions/{subscription_id}",
    response_model=responses.SubscriptionResponse,
    tags=["Manage Subscriptions"],
)
def get_subscription_details(
    subscription_id: UUID,
) -> responses.SubscriptionResponse:
    """Details about a subscription.

    Takes a subscription_id as input, executes
    :class:`usecases.GetSubscriptionDetails`.
    """
    found = uc_get_subscription_details.execute(subscription_id)
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscription_id} not found",
        )
    return found


@app.get(
    "/subscriptions/{subscription_id}/resource-types",
    response_model=responses.ResourceTypeListResponse,
    tags=["Manage Subscriptions"],
)
def get_subscription_resource_type_list(
    subscription_id: UUID,
) -> responses.ResourceTypeListResponse:
    """List of Resource Types supported by a Collection."""
    found = uc_get_subscription_resource_type_list.execute(subscription_id)
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscription_id} not found",
        )
    return found


@app.get(
    "/subscriptions/{subscription_id}/collections",
    response_model=responses.CollectionListResponse,
    tags=["Manage Subscriptions"],
)
def get_collection_list(
    subscription_id: UUID,
) -> responses.CollectionListResponse:
    """List of Collections under a Subscription."""
    found = uc_get_subscription_collection_list.execute(subscription_id)
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription with ID {subscription_id} not found",
        )
    return found


@app.post(
    "/subscriptions/{subscription_id}/collections",
    response_model=responses.CollectionResponse,
    tags=["Manage Subscriptions"],
)
def post_new_collection_to_subscription(
    subscription_id: UUID,
    new_collection: requests.NewCollectionRequest,
) -> responses.CollectionResponse:
    """Save a new collection to a Subscription."""
    created_collection = uc_post_new_collection_to_subscription.execute(
        subscription_id, new_collection
    )
    if created_collection:
        return created_collection
    else:
        msg = f"A colleciton called '{new_collection.name}' already exists"
        msg += f" for subscription '{subscription_id}'"
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)


@app.delete(
    "/subscriptions/{subscription_id}",
    response_model=responses.DeleteSubscriptionResponse,
    tags=["Manage Subscriptions"],
)
def delete_subscription(
    subscription_id: UUID,
) -> responses.DeleteSubscriptionResponse:
    """Remove the subscription

    and all it's Collections, and all their Resources.

    .. admonition:: This is a heavy thing to do

       Might want to put a safety switch on it (envar ENABLE_HEAVY_DELETES)
       and maybe a soft delete option (envar HEAVY_DELETES_SOFTLY)
    """
    response = uc_delete_subscription.execute(subscription_id)
    if response.success:
        return response

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=response.dict(),
    )


@app.get(
    "/collections/{collection_id}",
    response_model=responses.CollectionResponse,
    tags=["Manage Collections"],
)
def get_collection_details(
    collection_id: UUID,
) -> responses.CollectionResponse:
    """Details about a collection."""
    found = uc_get_collection_details.execute(collection_id)
    if found:
        return found
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection not found with id of '{collection_id}'",
        )


@app.get(
    "/resource-types/",
    response_model=responses.ResourceTypeListResponse,
    tags=["Manage Features"],
)
def get_resource_types() -> responses.ResourceTypeListResponse:
    return uc_get_resource_type_list.execute()


#
# stubs
#
@app.get(
    "/collections/{collection_id}/resource-types",
    response_model=responses.ResourceTypeListResponse,
    tags=["Manage Collections"],
)
def get_collection_resource_type_list(
    collection_id: UUID,
) -> responses.ResourceTypeListResponse:
    """List of resource-types supported by a collection.

    These are the types of resources that can be posted to the collection,
    and they are inherited from the subscription that the collection belongs to.
    """
    return uc_get_collection_resource_type_list.execute(collection_id)


@app.get(
    "/collections/{collection_id}/resources",
    response_model=responses.ResourceListResponse,
    tags=["Manage Collections"],
)
def get_resource_list(collection_id: UUID) -> responses.ResourceListResponse:
    """List of the Resources in a Collection."""
    return uc_get_resource_list.execute(collection_id)


@app.post(
    "/collections/{collection_id}/{resource_type_id}",
    response_model=responses.ResourceUploadResponse,
    tags=["Manage Collections"],
)
async def post_new_resource_to_collection(
    collection_id: UUID,
    resource_type_id: UUID,
    name: Optional[str] = Form(None),  # = "Clint Eastwood",
    webhooks: Optional[List[str]] = Form([]),
    # metadata: Optional[dict] = {},
    new_resource: UploadFile = File(
        ..., description="The file content to upload as a new resource"
    ),
) -> responses.ResourceUploadResponse:
    """Save a new resource in a collection,
    trigger background processing,
    and respond with the URL where the resource will be available.
    """
    binary_data = await new_resource.read()
    upload_request = requests.ResourceUploadRequest(
        file_name=new_resource.filename,
        file_content=binary_data,
        name=name,
        webhooks=webhooks,
        resource_type_id=resource_type_id,
        collection_id=collection_id,
        # metadata=metadata,
    )
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        uc_post_new_resource_to_collection.execute,
        upload_request,
    )


@app.delete(
    "/collections/{collection_id}",
    response_model=responses.DeleteCollectionResponse,
    tags=["Manage Collections"],
)
def delete_collection(
    collection_id: UUID,
) -> responses.DeleteCollectionResponse:
    """Remove the collection and it's resources.

    Also removes the queries, etc. This is a heavy thing to do,
    might want to put a safety switch on it (envar ENABLE_HEAVY_DELETES)
    and maybe a soft delete option (envar HEAVY_DELETES_SOFTLY).
    """
    deleted = uc_delete_collection.execute(collection_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection {collection_id} not found, unable to delete it",
        )
    return deleted


# # Resources
# @app.get(
#     "/resources/{resource_id}",
#     response_model=interfaces.ResourceResponse,
#     tags=["Manage Resources"],
# )
# def get_resource(resource_id: int) -> interfaces.ResourceResponse:
#     """Get Resource (file that was uploaded)."""
#     return uc_get_resource.execute(resource_id)


# @app.get(
#     "/resources/{resource_id}/metadata",
#     response_model=interfaces.ResourceMetadataResponse,
#     tags=["Manage Resources"],
# )
# def get_resource_metadata(
#     resource_id: int,
# ) -> interfaces.ResourceMetadataResponse:
#     """Get metadata about Resource."""
#     return uc_get_resource_metadata.execute(resource_id)


@app.delete(
    "/resources/{resource_id}",
    response_model=responses.DeleteResourceResponse,
    tags=["Manage Resources"],
)
def delete_resource(resource_id: int) -> responses.DeleteResourceResponse:
    """Remove a resource from it's collection.

    Also removes the queries associated with the resource.
    """
    return uc_delete_resource.execute(resource_id)


# Query Interfaces
@app.post(
    "/collections/{collection_id}/query",
    response_model=responses.QueryCollectionResponse,
    tags=["Semantic Queries"],
)
def query_collection(
    collection_id: UUID, query: requests.QueryCollectionRequest
) -> responses.QueryCollectionResponse:
    return uc_post_query_on_collection.execute(collection_id, query)


@app.post(
    "/resource/{resource_id}/query",
    response_model=responses.QueryResourceResponse,
    tags=["Semantic Queries"],
)
def query_resource(resource_id: int) -> responses.QueryResourceResponse:
    return uc_post_query_on_resource.execute(resource_id)


@app.get(
    "/query-results/{query_id}",
    response_model=responses.QueryResult,
    tags=["Semantic Queries"],
)
def get_query_result(query_id: int) -> responses.QueryResult:
    """
    Fetches a Query Result.
    """
    return uc_get_query_result.execute(query_id)


@app.get(
    "/query-results/{query_id}/metadata",
    response_model=responses.QueryResultMetadata,
    tags=["Semantic Queries"],
)
def get_query_result_metadata(query_id: int) -> responses.QueryResultMetadata:
    """Returns metadata about the query result.

    Will eventually include a Digital Product Passport (DPP)
    containing verifiable supply-chain provonance information
    about how the results were obtained.
    """
    return uc_get_query_result_metadata.execute(query_id)
