"""FastAPI application for Knowledge Hub Agent."""

import logging
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..agent import KnowledgeHubAgent, AgentConfig
from .config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global agent instance
agent: Optional[KnowledgeHubAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global agent

    # Startup
    settings = get_settings()

    # Initialize agent
    agent_config = AgentConfig(
        subscription_id=settings.azure_subscription_id,
        resource_group=settings.azure_resource_group,
        project_name=settings.azure_project_name,
        model=settings.agent_model,
        temperature=settings.agent_temperature,
        use_file_search=settings.use_file_search,
    )

    agent = KnowledgeHubAgent(config=agent_config)

    # Create or get vector store
    if settings.use_file_search:
        agent.create_vector_store()

    # Create agent
    agent.create_agent()

    logger.info("Application started successfully")

    yield

    # Shutdown
    if agent:
        agent.cleanup()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Knowledge Hub Agent API",
    description="API for querying product documentation using AI agents with RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class QueryRequest(BaseModel):
    """Query request model."""

    question: str = Field(..., description="Question to ask the agent")
    thread_id: Optional[str] = Field(
        None, description="Thread ID for conversation context"
    )
    instructions: Optional[str] = Field(
        None, description="Additional instructions for this query"
    )


class QueryResponse(BaseModel):
    """Query response model."""

    answer: str = Field(..., description="Agent response")
    thread_id: str = Field(..., description="Thread ID for this conversation")
    status: str = Field(..., description="Query status")


class UploadFilesRequest(BaseModel):
    """Upload files request model."""

    file_paths: List[str] = Field(
        ..., description="List of file paths to upload"
    )


class UploadFilesResponse(BaseModel):
    """Upload files response model."""

    file_ids: List[str] = Field(..., description="Uploaded file IDs")
    count: int = Field(..., description="Number of files uploaded")


class ThreadHistoryResponse(BaseModel):
    """Thread history response model."""

    messages: List[dict] = Field(
        ..., description="List of messages in the thread"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    agent_initialized: bool = Field(
        ..., description="Whether agent is initialized"
    )


# API endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None and agent.agent is not None,
    }


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Query the knowledge hub agent.

    Args:
        request: Query request with question and optional thread ID

    Returns:
        Agent response
    """
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized",
        )

    try:
        # Create thread if not provided
        thread_id = request.thread_id
        if not thread_id:
            thread = agent.create_thread()
            thread_id = thread.id

        # Query agent
        answer = agent.query(
            question=request.question,
            thread_id=thread_id,
            instructions=request.instructions,
        )

        return QueryResponse(
            answer=answer,
            thread_id=thread_id,
            status="success",
        )

    except Exception as e:
        logger.error(f"Error querying agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying agent: {str(e)}",
        )


@app.post("/upload-files", response_model=UploadFilesResponse)
async def upload_files(request: UploadFilesRequest):
    """Upload files to the vector store.

    Args:
        request: Upload files request with file paths

    Returns:
        Uploaded file IDs
    """
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized",
        )

    try:
        file_ids = agent.upload_files(
            file_paths=request.file_paths, update_vector_store=True
        )

        return UploadFilesResponse(
            file_ids=file_ids,
            count=len(file_ids),
        )

    except Exception as e:
        logger.error(f"Error uploading files: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading files: {str(e)}",
        )


@app.get("/threads/{thread_id}/history", response_model=ThreadHistoryResponse)
async def get_thread_history(thread_id: str):
    """Get conversation history for a thread.

    Args:
        thread_id: Thread ID

    Returns:
        List of messages in the thread
    """
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized",
        )

    try:
        messages = agent.get_thread_history(thread_id=thread_id)

        return ThreadHistoryResponse(messages=messages)

    except Exception as e:
        logger.error(f"Error getting thread history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting thread history: {str(e)}",
        )


@app.post("/threads/create")
async def create_thread():
    """Create a new conversation thread.

    Returns:
        Thread ID
    """
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent not initialized",
        )

    try:
        thread = agent.create_thread()
        return {"thread_id": thread.id}

    except Exception as e:
        logger.error(f"Error creating thread: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating thread: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
