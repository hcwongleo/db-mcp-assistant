#!/bin/bash
set -e
set -o pipefail

# AWS credentials should be configured via AWS CLI or environment variables
# Run 'aws configure' or set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
# export ISENGARD_PRODUCTION_ACCOUNT=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.10+ first."
        exit 1
    fi
    
    # Check CDK
    if ! command -v cdk &> /dev/null; then
        log_error "AWS CDK is not installed. Please install it first:"
        log_error "npm install -g aws-cdk"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    log_success "Prerequisites check completed"
}

# ----- Config -----
STACK_NAME=${1:-CdkAgentCoreStrandsDbMcpAssistantStack}
AGENT_NAME=${2:-db_mcp_assistant}
REGION=$(aws configure get region)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Check prerequisites first
check_prerequisites

echo "🚀 Starting DB MCP Assistant deployment..."
echo "📍 Region: $REGION"
echo "🏷️  Account ID: $ACCOUNT_ID"
echo "📦 CDK Stack: $STACK_NAME"
echo "🤖 Agent Name: $AGENT_NAME"
echo ""

# ----- 1. Deploy CDK Infrastructure -----
echo ""
log_info "Step 1: Deploying CDK Infrastructure..."
cd cdk-agentcore-strands-db-mcp-assistant

# Install CDK dependencies
log_info "Installing CDK dependencies..."
npm install

# Bootstrap CDK (if needed)
log_info "Bootstrapping CDK..."
cdk bootstrap || log_warning "CDK bootstrap failed or already done"

# Deploy CDK stack
log_info "Deploying CDK stack..."
if cdk deploy --require-approval never; then
    log_success "CDK infrastructure deployed successfully"
else
    log_error "CDK deployment failed"
    exit 1
fi

# Get CDK outputs
log_info "Retrieving CDK outputs..."
DSQL_CLUSTER_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='DSQLClusterArn'].OutputValue" --output text 2>/dev/null || echo "")
DSQL_CLUSTER_ID=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='DSQLClusterId'].OutputValue" --output text 2>/dev/null || echo "")
AGENT_CORE_ROLE=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='AgentCoreMyRoleARN'].OutputValue" --output text 2>/dev/null || echo "")

echo "   DSQL Cluster ARN: ${DSQL_CLUSTER_ARN:-Not found}"
echo "   DSQL Cluster ID: ${DSQL_CLUSTER_ID:-Not found}"
echo "   Agent Core Role: ${AGENT_CORE_ROLE:-Not found}"

cd ..

# ----- 2. Setup Python Environment -----
echo ""
log_info "Step 2: Setting up Python environment..."
cd agentcore-strands-db-mcp-assistant

if [ ! -d ".venv" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv .venv
fi

log_info "Activating virtual environment..."
source .venv/bin/activate

log_info "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# ----- 3. Setup Agent Runtime -----
echo ""
log_info "Step 3: Setting up Agent Runtime..."

# Clean up any existing agentcore configuration
log_info "Cleaning up existing agentcore configuration..."
rm -f .agentcore.yaml
rm -f .bedrock_agentcore.yaml

# Configure AgentCore
log_info "Configuring AgentCore..."
agentcore configure --entrypoint app.py -er "$AGENT_CORE_ROLE" --name "$AGENT_NAME"

# Launch AgentCore
log_info "Launching AgentCore..."
LAUNCH_OUTPUT=$(agentcore launch --auto-update-on-conflict 2>&1)
LAUNCH_EXIT_CODE=$?

echo "$LAUNCH_OUTPUT"

if [ $LAUNCH_EXIT_CODE -eq 0 ]; then
    log_success "AgentCore deployed successfully!"
    
    # Extract agent runtime ARN from launch output if available
    AGENT_RUNTIME_ARN=$(echo "$LAUNCH_OUTPUT" | grep -o 'arn:aws:bedrock-agentcore:[^[:space:]]*' | head -1)
    
    if [ -n "$AGENT_RUNTIME_ARN" ]; then
        echo "Agent Runtime ARN: $AGENT_RUNTIME_ARN"
        
        # Test the deployment
        log_info "Testing AgentCore deployment..."
        agentcore invoke '{"prompt": "Hello world!", "session_id": "test-session", "last_k_turns": 20}'
    else
        log_warning "Could not extract agent runtime ARN from launch output"
        log_info "You can test the agent later with:"
        echo "   agentcore invoke '{\"prompt\": \"Hello world!\", \"session_id\": \"test\"}'"
    fi
else
    log_error "AgentCore launch failed with exit code $LAUNCH_EXIT_CODE"
    log_info "You may need to run the launch command manually:"
    echo "   agentcore launch --auto-update-on-conflict"
fi

# ----- 4. Frontend Deployment -----
echo ""
log_info "Step 4: Deploying Frontend..."
cd ../frontend-db-mcp-assistant-agentcore-strands

log_info "Installing frontend dependencies..."
npm install

log_info "Configuring frontend with AgentCore ARN..."
# Get the Agent Runtime ARN from agentcore status
cd ../agentcore-strands-db-mcp-assistant
AGENT_ARN=$(agentcore status 2>/dev/null | grep "Agent Arn:" | sed 's/.*Agent Arn: //' | sed 's/ │.*//' | head -1 | xargs)
cd ../frontend-db-mcp-assistant-agentcore-strands

if [ -n "$AGENT_ARN" ]; then
    echo "Configuring frontend with Agent ARN: $AGENT_ARN"
    # Update the env.js file with the correct ARN
    sed -i.bak "s|const AGENT_RUNTIME_ARN = \".*\";|const AGENT_RUNTIME_ARN = \"$AGENT_ARN\";|" src/env.js
    log_success "Frontend configured with AgentCore ARN"
else
    log_warning "Could not retrieve Agent Runtime ARN"
fi

log_info "Building frontend..."
npm run build

# Check if port 3000 is already in use and kill the process
log_info "Checking for existing processes on port 3000..."
EXISTING_PID=$(lsof -ti:3000 2>/dev/null || echo "")
if [ -n "$EXISTING_PID" ]; then
    log_warning "Found process running on port 3000 (PID: $EXISTING_PID). Stopping it..."
    kill -9 $EXISTING_PID 2>/dev/null || true
    sleep 2
fi

log_info "Starting frontend development server..."
echo "Frontend will be available at: http://localhost:3000"
npm start &

log_success "Frontend deployed successfully!"
cd ../agentcore-strands-db-mcp-assistant
echo "🎉 Complete deployment finished!"
echo ""
echo "📋 Deployment Summary:"
echo "   ✅ CDK Infrastructure deployed"
echo "   ✅ AgentCore Agent deployed and running"
echo "   ✅ Frontend built and started"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   AgentCore: Use 'agentcore invoke' commands"
echo ""
echo "🧪 Test your agent:"
echo "   agentcore invoke '{\"prompt\": \"What tables are available?\", \"session_id\": \"test\"}'"
echo ""
echo "🧹 To clean up everything later:"
echo "   1. Stop frontend: pkill -f 'npm start'"
echo "   2. Destroy infrastructure: cd cdk-agentcore-strands-db-mcp-assistant && cdk destroy"