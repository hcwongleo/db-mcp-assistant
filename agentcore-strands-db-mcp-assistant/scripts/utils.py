"""
Utility functions for DSQL Assistant

This module provides utility functions including SSM parameter retrieval.
"""

import boto3
import os
from botocore.exceptions import ClientError

# Project ID for SSM parameter path prefix
PROJECT_ID = "agentcore-db-mcp-assistant"

# Default AWS region
DEFAULT_REGION = "us-east-1"

def get_ssm_client(region_name=None):
    """
    Creates and returns an SSM client.
    
    Args:
        region_name: AWS region where the SSM parameters are stored
        
    Returns:
        boto3.client: SSM client
    """
    if not region_name:
        region_name = os.environ.get("AWS_REGION", DEFAULT_REGION)
        
    session = boto3.session.Session()
    return session.client(service_name="ssm", region_name=region_name)

def get_ssm_parameter(param_name, region_name=None):
    """
    Retrieves a parameter from AWS Systems Manager Parameter Store.
    
    Args:
        param_name: Full parameter name (with or without leading slash)
        region_name: AWS region where the parameter is stored
        
    Returns:
        str: The parameter value
        
    Raises:
        ClientError: If there's an error retrieving the parameter
    """
    client = get_ssm_client(region_name)
    
    # Handle both full paths and short names
    if param_name.startswith('/'):
        full_param_name = param_name
    else:
        full_param_name = f"/{PROJECT_ID}/{param_name}"
    
    try:
        response = client.get_parameter(
            Name=full_param_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except ClientError as e:
        print(f"Error retrieving SSM parameter {full_param_name}: {e}")
        raise