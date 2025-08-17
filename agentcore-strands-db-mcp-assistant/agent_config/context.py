"""
DSQL Assistant Context Management

This module manages the context for the DSQL assistant, including
streaming queue and other shared state.
"""

from contextvars import ContextVar
from typing import Optional
from .streaming_queue import StreamingQueue


class DSQLAssistantContext:
    """Context manager for DSQL Assistant shared state"""
    
    _response_queue_ctx: ContextVar[Optional[StreamingQueue]] = ContextVar('response_queue', default=None)
    _gateway_token_ctx: ContextVar[Optional[str]] = ContextVar('gateway_token', default=None)
    _agent_ctx: ContextVar[Optional[object]] = ContextVar('agent', default=None)
    
    @classmethod
    def get_response_queue_ctx(cls) -> Optional[StreamingQueue]:
        """Get the current response queue from context"""
        return cls._response_queue_ctx.get()
    
    @classmethod
    def set_response_queue_ctx(cls, queue: StreamingQueue) -> None:
        """Set the response queue in context"""
        cls._response_queue_ctx.set(queue)
    
    @classmethod
    def get_gateway_token_ctx(cls) -> Optional[str]:
        """Get the current gateway token from context"""
        return cls._gateway_token_ctx.get()
    
    @classmethod
    def set_gateway_token_ctx(cls, token: str) -> None:
        """Set the gateway token in context"""
        cls._gateway_token_ctx.set(token)
    
    @classmethod
    def get_agent_ctx(cls) -> Optional[object]:
        """Get the current agent from context"""
        return cls._agent_ctx.get()
    
    @classmethod
    def set_agent_ctx(cls, agent: object) -> None:
        """Set the agent in context"""
        cls._agent_ctx.set(agent)