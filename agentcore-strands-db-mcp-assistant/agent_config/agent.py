from agent_config.memory_hook_provider import MemoryHook
from agent_config.tools.dsql_mcp_assistant import dsql_assistant
from strands import Agent
from strands_tools import think
from strands.models import BedrockModel
from typing import List


class DSQLAssistant:
    def __init__(
        self,
        memory_hook: MemoryHook,
        bedrock_model_id: str = "us.amazon.nova-pro-v1:0",
        system_prompt: str = None,
        tools: List[callable] = None,
    ):
        self.model_id = bedrock_model_id
        self.model = BedrockModel(
            model_id=self.model_id,
        )
        self.system_prompt = (
            system_prompt
            if system_prompt
            else """You are a DSQL Database Assistant, a sophisticated agent designed to help users interact with their DSQL database. Your role is to:

1. Analyze incoming queries and determine if they are database-related:
   - SQL queries and database operations
   - Data analysis requests
   - Schema exploration
   - Database administration tasks

2. Key Responsibilities:
   - Execute SQL queries against the DSQL database
   - Help users understand their data structure
   - Provide insights from query results
   - Assist with database operations

3. Decision Protocol:
   - If query involves database operations -> Use available database tools
   - If query is about data analysis -> Use available database tools
   - If query is not database-related -> Politely explain your role is database assistance

Always provide clear explanations of query results and help users understand their data.

You have been provided with database tools to help resolve user inquiries.

<guidelines>
- Never assume any parameter values while using database tools
- If you do not have the necessary information to process a request, politely ask the user for the required details
- Always maintain a professional and helpful tone when assisting users
- Focus on resolving the user's database inquiries efficiently and accurately
- Provide clear explanations of query results and data insights
</guidelines>"""
        )

        # Use only the dsql_assistant tool (which handles MCP client internally)
        self.tools = (
            [
                think,
                dsql_assistant,
            ]
            + (tools or [])
        )
        
        self.memory_hook = memory_hook
        self.agent = Agent(
            model=self.model,
            system_prompt=self.system_prompt,
            tools=self.tools,
            hooks=[self.memory_hook],
        )

    def invoke(self, user_query: str):
        try:
            response = str(self.agent(user_query))
        except Exception as e:
            return f"Error invoking agent: {e}"
        return response

    async def stream(self, user_query: str):
        try:
            async for event in self.agent.stream_async(user_query):
                if "data" in event:
                    # Only stream text chunks to the client
                    yield event["data"]
        except Exception as e:
            yield f"We are unable to process your request at the moment. Error: {e}"