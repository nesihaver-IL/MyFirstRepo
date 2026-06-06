@echo off
REM Initialize Knowledge Hub Agent - Create Vector Store and Agent

echo ============================================
echo Initializing Knowledge Hub Agent
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

echo Creating vector store and agent...
echo This may take a few minutes...
echo.

python -c "from src.agent import KnowledgeHubAgent, AgentConfig; import os; from dotenv import load_dotenv; load_dotenv(); config = AgentConfig(subscription_id=os.getenv('AZURE_SUBSCRIPTION_ID'), resource_group=os.getenv('AZURE_RESOURCE_GROUP'), project_name=os.getenv('AZURE_PROJECT_NAME')); agent = KnowledgeHubAgent(config); print('Creating vector store...'); agent.create_vector_store(); print('Vector store created!'); print('Creating agent...'); agent.create_agent(); print('Agent created successfully!');"

if errorlevel 1 (
    echo [ERROR] Initialization failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo Initialization Complete!
echo ============================================
echo.
echo Vector store and agent have been created.
echo.
echo Next steps:
echo 1. Add documentation files to the 'docs' folder
echo 2. Run: upload-docs.bat (to upload documentation)
echo 3. Run: run.bat (to start the API server)
echo.
pause
