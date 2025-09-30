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
