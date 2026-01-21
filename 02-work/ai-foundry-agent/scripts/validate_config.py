#!/usr/bin/env python3
"""
Configuration Validation Script

Validates that all required configuration is set correctly
before deploying or running the Knowledge Hub Agent.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple

def load_env_file() -> bool:
    """Load .env file if it exists."""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        return False
    
    try:
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes
                    value = value.strip('"').strip("'")
                    os.environ[key] = value
        return True
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def validate_required_vars() -> Tuple[List[str], List[str]]:
    """Validate required environment variables."""
    errors = []
    warnings = []
    
    # Required variables
    required = {
        'AZURE_SUBSCRIPTION_ID': {
            'desc': 'Azure subscription ID (UUID format)',
            'pattern': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        },
        'AZURE_RESOURCE_GROUP': {
            'desc': 'Resource group name',
            'pattern': r'^[a-zA-Z0-9_\-\.]+$'
        },
        'AZURE_PROJECT_NAME': {
            'desc': 'AI Foundry project name',
            'pattern': r'^[a-zA-Z0-9_\-]+$'
        }
    }
    
    for var, config in required.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"❌ {var} is not set ({config['desc']})")
        elif value.startswith('<') or value.startswith('your-') or value == '':
            errors.append(f"❌ {var} has placeholder value: {value}")
        elif 'pattern' in config and not re.match(config['pattern'], value, re.IGNORECASE):
            errors.append(f"❌ {var} has invalid format: {value}")
    
    # Optional but recommended
    optional = {
        'AGENT_MODEL': 'gpt-4o',
        'AGENT_TEMPERATURE': '0.3',
        'USE_FILE_SEARCH': 'true',
        'API_PORT': '8000',
        'LOG_LEVEL': 'INFO'
    }
    
    for var, default in optional.items():
        if not os.getenv(var):
            warnings.append(f"⚠️  {var} not set (will use default: {default})")
    
    return errors, warnings

def validate_azure_cli() -> List[str]:
    """Check if Azure CLI is installed and configured."""
    errors = []
    
    # Check Azure CLI installed
    if os.system('which az > /dev/null 2>&1') != 0:
        errors.append("❌ Azure CLI not installed")
        errors.append("   Install: https://docs.microsoft.com/cli/azure/install-azure-cli")
        return errors
    
    # Check logged in
    if os.system('az account show > /dev/null 2>&1') != 0:
        errors.append("❌ Not logged in to Azure CLI")
        errors.append("   Run: az login")
    
    return errors

def validate_python_packages() -> List[str]:
    """Validate required Python packages are installed."""
    errors = []
    
    required_packages = [
        'azure.ai.projects',
        'azure.search.documents',
        'fastapi',
        'pydantic'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            errors.append(f"❌ Python package '{package}' not installed")
    
    if errors:
        errors.append("   Run: pip install -r requirements.txt")
    
    return errors

def main():
    """Main validation function."""
    print("🔍 Validating Knowledge Hub Agent Configuration...\n")
    
    all_errors = []
    all_warnings = []
    
    # 1. Load .env file
    print("1. Checking .env file...")
    if not load_env_file():
        sys.exit(1)
    print("   ✅ .env file loaded\n")
    
    # 2. Validate environment variables
    print("2. Validating environment variables...")
    errors, warnings = validate_required_vars()
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for error in errors:
            print(f"   {error}")
    else:
        print("   ✅ All required variables are set")
    print()
    
    # 3. Validate Azure CLI
    print("3. Checking Azure CLI...")
    errors = validate_azure_cli()
    all_errors.extend(errors)
    if errors:
        for error in errors:
            print(f"   {error}")
    else:
        print("   ✅ Azure CLI is configured")
    print()
    
    # 4. Validate Python packages
    print("4. Checking Python packages...")
    errors = validate_python_packages()
    all_errors.extend(errors)
    if errors:
        for error in errors:
            print(f"   {error}")
    else:
        print("   ✅ All required packages are installed")
    print()
    
    # Summary
    print("=" * 60)
    if all_errors:
        print(f"❌ VALIDATION FAILED: {len(all_errors)} error(s) found")
        print("\nErrors:")
        for error in all_errors:
            print(f"  {error}")
        sys.exit(1)
    elif all_warnings:
        print(f"⚠️  VALIDATION PASSED with {len(all_warnings)} warning(s)")
        print("\nWarnings:")
        for warning in all_warnings:
            print(f"  {warning}")
        sys.exit(0)
    else:
        print("✅ VALIDATION PASSED: Configuration is valid")
        sys.exit(0)

if __name__ == '__main__':
    main()
