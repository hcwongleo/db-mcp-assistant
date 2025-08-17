"""
Memory Hook Provider for DSQL Assistant

This module provides memory hook functionality following the 
HR assistant pattern.
"""

import logging
from strands.hooks.events import AgentInitializedEvent, MessageAddedEvent
from strands.hooks.registry import HookProvider, HookRegistry
from bedrock_agentcore.memory import MemoryClient

logger = logging.getLogger(__name__)


class MemoryHook(HookProvider):
    """
    Memory hook provider for DSQL Assistant.
    """
    
    def __init__(self, memory_client: MemoryClient, memory_id: str, actor_id: str, session_id: str, last_k_turns: int = 10):
        """
        Initialize the memory hook provider.
        
        Args:
            memory_client: Client for interacting with Bedrock Agent Core memory
            memory_id: ID of the memory resource
            actor_id: ID of the user/actor
            session_id: ID of the current conversation session
            last_k_turns: Number of conversation turns to retrieve from history
        """
        self.memory_client = memory_client
        self.memory_id = memory_id
        self.actor_id = actor_id
        self.session_id = session_id
        self.last_k_turns = last_k_turns
    
    def on_agent_initialized(self, event: AgentInitializedEvent):
        """
        Load recent conversation history when agent starts.
        
        Args:
            event: Agent initialization event
        """
        try:
            recent_turns = self.memory_client.get_last_k_turns(
                memory_id=self.memory_id,
                actor_id=self.actor_id,
                session_id=self.session_id,
                k=self.last_k_turns
            )
            
            if recent_turns:
                context_messages = []
                for turn in recent_turns:
                    for message in turn:
                        role = message['role']
                        content = message['content']['text']
                        context_messages.append(f"{role}: {content}")
                
                context = "\n".join(context_messages)
                event.agent.system_prompt += f"\n\nRecent conversation:\n{context}"
                logger.info(f"✅ Loaded {len(recent_turns)} conversation turns")
                
        except Exception as e:
            logger.error(f"Memory load error: {e}")
    
    def on_message_added(self, event: MessageAddedEvent):
        """
        Store messages in memory as they are added to the conversation.
        
        Args:
            event: Message added event
        """
        try:
            messages = event.agent.messages
            last_message = messages[-1]
            
            if "role" in last_message and "content" in last_message and last_message["content"]:
                role = last_message["role"]
                
                content_to_save = None
                for content_item in last_message["content"]:
                    if "text" in content_item:
                        content_to_save = content_item["text"]
                        break
                
                if content_to_save:
                    self.memory_client.save_conversation(
                        memory_id=self.memory_id,
                        actor_id=self.actor_id,
                        session_id=self.session_id,
                        messages=[(content_to_save, role)]
                    )
                    logger.info("Message saved to memory")
                    
        except Exception as e:
            logger.error(f"Memory save error: {e}")
    
    def register_hooks(self, registry: HookRegistry):
        """
        Register memory hooks with the hook registry.
        
        Args:
            registry: Hook registry to register with
        """
        registry.add_callback(MessageAddedEvent, self.on_message_added)
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)