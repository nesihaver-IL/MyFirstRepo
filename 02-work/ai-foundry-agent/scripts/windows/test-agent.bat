@echo off
REM Test the Knowledge Hub Agent with sample queries

echo ============================================
echo Testing Knowledge Hub Agent
echo ============================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found. Run setup-windows.bat first.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found. Please create it from .env.example
    pause
    exit /b 1
)

echo Running test queries...
echo.

python -c "from src.agent import KnowledgeHubAgent, AgentConfig; import os; from dotenv import load_dotenv; load_dotenv(); config = AgentConfig(subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'), resource_group=os.getenv('AZURE_RESOURCE_GROUP'), project_name=os.getenv('AZURE_PROJECT_NAME')); agent = KnowledgeHubAgent(config); print('Testing agent with sample query...'); print(); response = agent.query('What is this product about?'); print('Response:'); print(response);"

echo.
echo ============================================
echo Test Complete!
echo ============================================
echo.
pause
