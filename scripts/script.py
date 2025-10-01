import os
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal, List
from typing_extensions import Annotated
from pydantic.functional_validators import BeforeValidator
from pymongo import AsyncMongoClient
from pymongo.errors import BulkWriteError


# Load environment variables from .env file
load_dotenv(find_dotenv())
MONGO_URI = os.getenv("MONGO_URI")



# Async MongoDB client setup
client = AsyncMongoClient(MONGO_URI)
db = client["chunkDB"]
chunks_collection = db.get_collection("chunks")

# Set up MongoDB schema/collections for chunks and metadata.
class ChunkSchema(BaseModel):
    chunkId: str 
    source: Literal["code", "specification", "documentation"]
    chunk: str
    project: str
    repo: str
    section: str
    file: str
    version: str
    isEmbedded: bool = False

# Function to insert a single chunk into the MongoDB collection with validation.
async def insert_chunk(chunk_data: dict) -> str | None:
    """
    Insert a single chunk.
    Returns inserted ID.
    """
    chunk = ChunkSchema(**chunk_data)
    if await chunks_collection.find_one({"chunkId": chunk.chunkId}):
        print(f"Chunk with chunkId '{chunk.chunkId}' already exists.")
        return None
    result = await chunks_collection.insert_one(chunk.model_dump())
    return chunk.chunkId

# Function to insert many chunks into the MongoDB collection with validation.
async def insert_chunks(chunks_data: List[dict]) -> List[str]:
    """
    Insert multiple chunks with duplicate checking.
    Returns a list of inserted chunkIds.
    """
    valid_chunks = []

    # Validate and check duplicates
    for chunk_data in chunks_data:
        try:
            chunk = ChunkSchema(**chunk_data)
            if not await chunks_collection.find_one({"chunkId": chunk.chunkId}):
                valid_chunks.append(chunk.model_dump())
            else:
                print(f"Skipping duplicate chunkId: {chunk.chunkId}")
        except Exception as e:
            print("Validation error:", e)

    if not valid_chunks:
        return []

    # Insert many
    try:
        result = await chunks_collection.insert_many(valid_chunks, ordered=False)
        inserted_ids = result.inserted_ids
    except BulkWriteError as e:
        print("Some duplicates were skipped.", e.details)
        inserted_ids = e.details.get("writeErrors", [])
        # Extract inserted ids if available
        inserted_ids = [item["op"]["chunkId"] for item in inserted_ids if "op" in item and "chunkId" in item["op"]]

    # Return list of inserted chunkIds
    return [chunk["chunkId"] for chunk in valid_chunks]


# Function to retrieve  chunks by ChunkId from the MongoDB collection.
async def get_chunk_by_id(chunk_id: str) -> dict | None:
    """ 
    Retrieve a chunk by its ID.
    """
    return await chunks_collection.find_one({"chunkId": chunk_id}, {"_id": 0})
