#!/usr/bin/env python3
"""Type definitions for embedding input worker."""
from typing import TypedDict, Any, Optional, Union


class EmbeddingInputRequired(TypedDict):
    """Required fields for an embedding input message."""
    id: Union[int, str]
    text: str
    timestamp: int  # Unix epoch seconds (producer side)


class EmbeddingInputMessage(EmbeddingInputRequired, total=False):
    """
    Full embedding input message.
    Additional arbitrary fields are allowed (metadata, source, etc.).
    Example:
        {
            "id": 123,
            "text": "Some text to embed",
            "timestamp": 1723632000,
            "source": "ingestion-job-7",
            "metadata": {"lang": "en"}
        }
    """
    metadata: Any
    source: str
    trace_id: str
    # Add other optional fields as needed


ProcessedEmbedding = TypedDict('ProcessedEmbedding', {
    'id': Union[int, str],
    'vector_dim': int,
    'processing_duration': float,
    'ok': bool,
    'error': Optional[str],
})

