"""
Streaming Queue for DSQL Assistant

This module provides a streaming queue for handling asynchronous
response streaming in the DSQL assistant.
"""

import asyncio
from typing import AsyncGenerator, Any


class StreamingQueue:
    """Async queue for streaming responses"""
    
    def __init__(self):
        self._queue = asyncio.Queue()
        self._finished = False
    
    async def put(self, item: Any) -> None:
        """Add an item to the queue"""
        if not self._finished:
            await self._queue.put(item)
    
    async def finish(self) -> None:
        """Mark the queue as finished"""
        self._finished = True
        await self._queue.put(None)  # Sentinel value
    
    async def stream(self) -> AsyncGenerator[Any, None]:
        """Stream items from the queue"""
        while True:
            item = await self._queue.get()
            if item is None:  # Sentinel value indicates end
                break
            yield item