from .context import DSQLAssistantContext
from .memory_hook_provider import MemoryHook
from scripts.utils import get_ssm_parameter
from agent_config.agent import DSQLAssistant
from bedrock_agentcore.memory import MemoryClient
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

memory_client = MemoryClient()

async def agent_task(user_message: str, session_id: str, actor_id: str):
    agent = DSQLAssistantContext.get_agent_ctx()
    response_queue = DSQLAssistantContext.get_response_queue_ctx()
    gateway_access_token = DSQLAssistantContext.get_gateway_token_ctx()
    
    try:
        if agent is None:
            memory_hook = MemoryHook(
                memory_client=memory_client,
                memory_id=get_ssm_parameter("/agentcore-db-mcp-assistant/MEMORY_ID"),
                actor_id=actor_id,
                session_id=session_id,
            )
            
            agent = DSQLAssistant(
                memory_hook=memory_hook,
            )
            DSQLAssistantContext.set_agent_ctx(agent)
        
        async for chunk in agent.stream(user_query=user_message):
            await response_queue.put(chunk)
            
    except Exception as e:
        logger.exception("Agent execution failed.")
        await response_queue.put(f"Error: {str(e)}")
    finally:
        await response_queue.finish()