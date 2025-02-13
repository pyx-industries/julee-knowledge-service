import json

import pandas as pd
import requests
from neo4j import GraphDatabase

csv_file_path = "../gov_graph.csv"
dummy_file = "~/QubesIncoming/pyx/"
uri = "bolt://localhost:7687"
username = "neo4j"
password = "neo4j_psx"
API_URL = "http://localhost:8001"
HEADERS = {"Authorization": "Bearer we-dont-need-no-stinkin-authorization"}
SID = "b6a8d366-00d4-49e3-9853-f42d0e569f73"
RTID = "6ef0456b-0df9-4dd5-b6a3-e382e74c9cc7"


def get_collection_by_name(collection_name):
    response = requests.get(
        f"{API_URL}/subscriptions/{SID}/collections",
        headers=HEADERS,
        # params={"name": collection_name}
    )
    if response.status_code == 200:
        collections = response.json().get("collections", [])
        for collection in collections:
            if collection["name"] == collection_name:
                return collection
    return None


def create_collection(collection_name):
    new_collection_data = {
        "name": collection_name,
        "resource_type_ids": [
            RTID,
        ],
        "description": "New collection created via API",
    }
    response = requests.post(
        f"{API_URL}/subscriptions/{SID}/collections",
        headers=HEADERS,
        data=json.dumps(new_collection_data),
    )
    if response.status_code == 200:
        return response.json().get("id")
    else:
        print(f"Error creating collection: {response.text}")
        print(new_collection_data)
        print(response.status_code)
        print(f"{API_URL}/collections")
        raise Exception("that didn't work")


def get_resource_in_collection(collection_id, resource_name):
    response = requests.get(
        f"{API_URL}/collections/{collection_id}/resources", headers=HEADERS
    )
    if response.status_code == 200:
        resources = response.json().get("resources", [])
        for resource in resources:
            if resource["name"] == resource_name:
                return resource["id"]
    return None


def create_resource_in_collection(
    collection_id, collection_name, resource_name, webhooks=[]
):
    # FIXME: use actual files :)
    # check for them in the NextCloud places - print warning if they are
    # not there so that I can maintain alignment with the spreadsheet
    # (governance)
    file_path = "/home/user/QubesIncoming/pyx/OECD_typology.pdf"
    with open(file_path, "rb") as file:
        files = {
            "new_resource": (file_path, file, "application/octet-stream"),
        }
        url = f"{API_URL}/collections/{collection_id}/{RTID}"
        data = {
            "file_name": file_path,
            "name": resource_name,
        }
        response = requests.post(
            url,
            headers=HEADERS,
            files=files,
            data=data,
        )
    if response.status_code == 200:
        return response.json().get("id")
    else:
        print(f"Error creating resource: {response.text}")
        raise Exception("Error in request.")


query = """
MERGE (s:Subscription {subscription_id: "b6a8d366-00d4-49e3-9853-f42d0e569f73"})
MERGE (r:Resource {file_name: $file_name})
MERGE (c:Collection {name: $group_type})
MERGE (s)-[:INCLUDES]->(c)
MERGE (c)-[:CONTAINS]->(r)
RETURN r, c
"""
owner_query = """
MERGE (o:Owner {name: $owner_name})
MERGE (o)-[:OWNS]->(r:Resource {file_name: $file_name})
"""

# proposer_query
# status_query


def process_through_api(row):
    # use the API to generate uuids and pre-populate neo4j.
    collection_name = row["Group / Type"]
    resource_name = row["Document Name/Title"]

    collection = get_collection_by_name(collection_name)
    if collection is None:
        print(f"Collection '{collection_name}' not found. Creating it...")
        collection = create_collection(collection_name)
    collection_id = collection["id"]

    resource_id = get_resource_in_collection(collection_id, resource_name)
    if resource_id is None:
        print(
            f"Checking API: / {collection_name}/{resource_name}: not found, "
            "uploading it ..."
        )
        create_resource_in_collection(
            collection_id, collection_name, resource_name
        )
    else:
        print(f"Checking API: /{collection_name}/{resource_name}:  ... OK")


def process_through_graph(row):
    # now shoehorn the governance graph into neo4j
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        print(
            f"Processing Governance Graph ({row['Group / Type']})"
            f"-[CONTAINS]->({row['Document Name/Title']})"
        )
        result = session.run(
            query,
            file_name=row["Document Name/Title"],
            group_type=row["Group / Type"],
        )
        if row.get("Owner") and pd.notna(row["Owner"]):
            print(
                f"Processing Governance Graph: ({row['Owner']})"
                f"-[OWNS]->({row['Document Name/Title']})"
            )
            session.run(
                owner_query,
                owner_name=row["Owner"],
                file_name=row["Document Name/Title"],
            )
        return result.single() is not None


if __name__ == "__main__":
    df = pd.read_csv(csv_file_path)
    stage_1 = df.apply(process_through_api, axis=1)
    stage_2 = df.apply(process_through_graph, axis=1)
    print(f"Processed through API: {stage_1.sum()}")
    print(f"Processed through Graph: {stage_2.sum()}")
    # for col in df.columns:
    #     print(col)
