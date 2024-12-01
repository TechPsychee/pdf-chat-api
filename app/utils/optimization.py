from typing import List, Dict
import asyncio
from ..core.config import get_settings

settings = get_settings()


async def chunk_text(text: str) -> List[str]:
    """Split text into manageable chunks"""
    chunks = []
    length = len(text)
    for i in range(0, length, settings.CHUNK_SIZE):
        chunk = text[i : i + settings.CHUNK_SIZE]
        chunks.append(chunk)
    return chunks


async def process_large_document(text: str) -> List[Dict]:
    """Process large documents in chunks"""
    chunks = await chunk_text(text)

    if len(chunks) > settings.MAX_CHUNKS_PER_REQUEST:
        raise ValueError("Document too large to process")

    tasks = []
    for chunk in chunks:
        task = asyncio.create_task(process_chunk(chunk))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results


async def process_chunk(chunk: str) -> Dict:
    """Process individual chunk of text"""
    # Add your processing logic here
    return {"chunk_size": len(chunk), "processed": True}
