#!/bin/bash

# Garmin Connect Integration - Quick Start Script
# This script helps you set up Garmin Connect integration quickly

set -e

echo "========================================="
echo "Garmin Connect Integration Quick Start"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python installation
echo -e "${YELLOW}Step 1: Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python is installed: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3 is not installed. Please install Python 3.8+${NC}"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
echo -e "${YELLOW}Step 2: Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Step 3: Activate virtual environment
echo ""
echo -e "${YELLOW}Step 3: Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Step 4: Install dependencies
echo ""
echo -e "${YELLOW}Step 4: Installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install garminconnect boto3 python-dotenv > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed:${NC}"
echo "  - garminconnect (Garmin API client)"
echo "  - boto3 (AWS SDK)"
echo "  - python-dotenv (Environment variables)"

# Step 5: Create .env file
echo ""
echo -e "${YELLOW}Step 5: Setting up credentials...${NC}"
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Garmin Connect Credentials
# WARNING: Never commit this file to git!

GARMIN_EMAIL=your@email.com
GARMIN_PASSWORD=your_password_here

# AWS Configuration (optional for local testing)
AWS_REGION=us-east-1
AWS_PROFILE=default

# DynamoDB Table Names (if using AWS)
DYNAMODB_ACTIVITIES_TABLE=HealthInsights-Activities
DYNAMODB_SLEEP_TABLE=HealthInsights-SleepData
DYNAMODB_MEMORY_TABLE=HealthInsights-UserMemory
EOF
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}  → Please edit .env and add your Garmin credentials${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Step 6: Add .env to .gitignore
echo ""
echo -e "${YELLOW}Step 6: Updating .gitignore...${NC}"
if [ -f ".gitignore" ]; then
    if ! grep -q "^\.env$" .gitignore; then
        echo ".env" >> .gitignore
        echo "venv/" >> .gitignore
        echo "*.pyc" >> .gitignore
        echo "__pycache__/" >> .gitignore
        echo -e "${GREEN}✓ Added .env to .gitignore${NC}"
    else
        echo -e "${GREEN}✓ .env already in .gitignore${NC}"
    fi
else
    cat > .gitignore << 'EOF'
# Environment variables
.env

# Python
venv/
*.pyc
__pycache__/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
    echo -e "${GREEN}✓ Created .gitignore${NC}"
fi

# Step 7: Create test script
echo ""
echo -e "${YELLOW}Step 7: Creating test script...${NC}"
cat > test_garmin.py << 'EOF'
#!/usr/bin/env python3
"""
Quick test script for Garmin Connect integration
"""

import os
from dotenv import load_dotenv
from garminconnect import Garmin, GarminConnectAuthenticationError

# Load environment variables
load_dotenv()

def main():
    email = os.getenv('GARMIN_EMAIL')
    password = os.getenv('GARMIN_PASSWORD')

    if not email or not password or email == 'your@email.com':
        print("❌ Please update your .env file with Garmin credentials")
        print("   Edit the .env file and add your email and password")
        return

    print("🔄 Connecting to Garmin Connect...")

    try:
        # Initialize client
        client = Garmin(email, password)

        # Login
        client.login()
        print("✅ Successfully authenticated!")

        # Get user info
        full_name = client.get_full_name()
        print(f"\n👤 User: {full_name}")

        # Get recent activities
        print("\n📊 Fetching recent activities...")
        activities = client.get_activities(0, 10)

        if activities:
            print(f"✅ Found {len(activities)} recent activities:\n")
            for i, activity in enumerate(activities[:5], 1):
                activity_name = activity.get('activityName', 'Unnamed')
                activity_type = activity.get('activityType', {}).get('typeKey', 'unknown')
                start_time = activity.get('startTimeLocal', 'N/A')
                distance = activity.get('distance', 0)

                if distance > 0:
                    if 'swimming' in activity_type.lower():
                        distance_str = f"{distance:.0f}m"
                    else:
                        distance_str = f"{distance/1000:.2f}km"
                else:
                    distance_str = "N/A"

                print(f"  {i}. {activity_name}")
                print(f"     Type: {activity_type} | Distance: {distance_str} | Date: {start_time}")
                print()
        else:
            print("⚠️  No activities found")

        # Get today's sleep data
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')

        print(f"😴 Fetching sleep data for {today}...")
        try:
            sleep_data = client.get_sleep_data(today)
            if sleep_data:
                total_hours = sleep_data.get('sleepTimeSeconds', 0) / 3600
                print(f"✅ Total sleep: {total_hours:.2f} hours")

                sleep_score = sleep_data.get('sleepScores', {})
                if sleep_score:
                    overall_score = sleep_score.get('overall', {}).get('value', 'N/A')
                    print(f"   Sleep score: {overall_score}")
            else:
                print("⚠️  No sleep data available for today")
        except Exception as e:
            print(f"⚠️  Could not fetch sleep data: {e}")

        print("\n✅ Test completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Check out garmin_integration_example.py for full implementation")
        print("   2. See garmin_health_api_guide.md for all integration options")
        print("   3. Run 'python garmin_integration_example.py' for AWS Lambda example")

    except GarminConnectAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your email and password in .env")
        print("   2. Make sure 2FA is disabled or use app-specific password")
        print("   3. Try logging in at https://connect.garmin.com first")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
EOF

chmod +x test_garmin.py
echo -e "${GREEN}✓ Created test_garmin.py${NC}"

# Step 8: Summary
echo ""
echo "========================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "========================================="
echo ""
echo "📋 What was created:"
echo "   - Python virtual environment (venv/)"
echo "   - .env file for credentials"
echo "   - test_garmin.py for quick testing"
echo "   - Updated .gitignore"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "   1. Edit the .env file with your Garmin credentials:"
echo "      ${YELLOW}nano .env${NC}"
echo ""
echo "   2. Run the test script:"
echo "      ${YELLOW}source venv/bin/activate${NC}"
echo "      ${YELLOW}python test_garmin.py${NC}"
echo ""
echo "   3. Explore the examples:"
echo "      ${YELLOW}python garmin_integration_example.py${NC}"
echo ""
echo "   4. Read the full guide:"
echo "      ${YELLOW}cat garmin_health_api_guide.md${NC}"
echo ""
echo "⚠️  Security Reminder:"
echo "   - Never commit .env to git"
echo "   - Use AWS Secrets Manager for production"
echo "   - Consider 2FA for your Garmin account"
echo ""
echo "📚 Documentation:"
echo "   - garmin_integration_example.py - Full Python implementation"
echo "   - garmin_health_api_guide.md - Complete integration guide"
echo "   - HEALTH_INSIGHTS_AGENT_PLAN.md - AWS Bedrock agent plan"
echo ""
echo "Happy coding! 🎉"
echo ""
