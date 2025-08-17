import os
import logging
from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@tool
def dsql_assistant(query: str) -> str:
    """
    Process and respond to DSQL database queries.
    
    Args:
        query: The user's SQL question
        
    Returns:
        A helpful response addressing the user query
    """
    # Use INFO level for key events to ensure they appear in AgentCore logs
    logger.info(f"🔍 DSQL Assistant called with query: {query}")
    
    try:
        logger.info("🤖 Creating Bedrock model...")
        bedrock_model = BedrockModel(model_id="us.amazon.nova-pro-v1:0")
        logger.info("✅ Bedrock model created successfully")
        response = str()
    except Exception as e:
        logger.error(f"❌ Failed to create Bedrock model: {e}")
        return f"Error creating Bedrock model: {str(e)}"
    
    try:
        # Import SSM utils inside the function to avoid loading at import time
        logger.info("📦 Importing SSM utils...")
        import sys
        import os
        # Add project root to Python path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        sys.path.insert(0, project_root)
        logger.info(f"📁 Added to Python path: {project_root}")
        
        from scripts.utils import get_ssm_parameter
        logger.info("✅ SSM utils imported successfully")
        
        # Get DSQL configuration when the function is called, not at import time
        logger.info("🔐 Retrieving DSQL configuration from SSM...")
        dsql_cluster_id = get_ssm_parameter("/agentcore-db-mcp-assistant/DSQL_CLUSTER_ID")
        logger.info(f"🆔 DSQL_CLUSTER_ID: {dsql_cluster_id}")
        
        aws_region = get_ssm_parameter("/agentcore-db-mcp-assistant/AWS_REGION")
        logger.info(f"🌍 AWS_REGION: {aws_region}")
        
        # Construct the cluster endpoint
        cluster_endpoint = f"{dsql_cluster_id}.dsql.{aws_region}.on.aws"
        logger.info(f"🔗 Cluster endpoint: {cluster_endpoint}")
        
        # Create MCP client with debug logging
        logger.info("🔌 Creating MCP client...")
        command_args = [
            "awslabs.aurora-dsql-mcp-server@latest",
            "--cluster_endpoint", cluster_endpoint,
            "--database_user", "admin",
            "--region", aws_region
        ]
        logger.info(f"⚡ MCP command: uvx {' '.join(command_args)}")
        
        dsql_mcp_server = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx",
                    args=command_args,
                )
            )
        )
        logger.info("✅ MCP client created successfully")
        
        logger.info("🔗 Connecting to MCP server...")
        with dsql_mcp_server:
            logger.info("✅ MCP server connection established")
            
            logger.info("🛠️ Listing available tools...")
            tools = dsql_mcp_server.list_tools_sync()
            logger.info(f"✅ Retrieved {len(tools)} tools")
            
            # Create the DSQL agent with specific capabilities
            logger.info("🤖 Creating DSQL agent...")
            dsql_agent = Agent(
                model=bedrock_model,
                system_prompt="""You are a helpful SQL assistant that can execute SQL queries against a DSQL database.
You can help users write and execute SQL queries to analyze their data.
Use the available database tools to run SQL queries when needed.
Provide clear explanations of query results and help users understand their data.

""",
                tools=tools,
            )
            logger.info("✅ DSQL agent created successfully")
            
            logger.info("⚡ Processing query with agent...")
            response = str(dsql_agent(query))
            logger.info(f"✅ Agent response received (length: {len(response)})")
            
            if len(response) > 0:
                logger.info("🎉 Returning successful response")
                return response
            
            logger.warning("⚠️ Empty response from agent")
            return "I apologize, but I couldn't properly analyze your question. Could you please rephrase or provide more context?"
            
    except Exception as e:
        logger.error(f"❌ Error in dsql_assistant: {str(e)}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        return f"Error processing your query: {str(e)}"

