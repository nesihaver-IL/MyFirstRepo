"""Agent configuration."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration for the Knowledge Hub Agent."""

    # Azure AI Foundry settings
    subscription_id: str = Field(..., description="Azure subscription ID")
    resource_group: str = Field(..., description="Azure resource group name")
    project_name: str = Field(..., description="AI Foundry project name")

    # Agent settings
    agent_name: str = Field(
        default="product-knowledge-hub",
        description="Name of the agent",
    )
    model: str = Field(
        default="gpt-4o",
        description="Model deployment name",
    )
    instructions: str = Field(
        default=(
            "You are a knowledgeable product documentation assistant. "
            "Your role is to help users find information about our products "
            "by searching through documentation, guides, and knowledge base articles. "
            "Always provide accurate, helpful, and well-structured responses based on the documentation. "
            "If you cannot find the answer in the documentation, clearly state that. "
            "Include relevant citations and references when possible."
        ),
        description="System instructions for the agent",
    )

    # Vector store settings
    use_vector_store: bool = Field(
        default=True,
        description="Whether to use Azure AI Search vector store",
    )
    search_endpoint: Optional[str] = Field(
        default=None,
        description="Azure AI Search endpoint URL",
    )
    search_index: str = Field(
        default="product-knowledge-base",
        description="Search index name",
    )

    # File search settings (built-in AI Foundry feature)
    use_file_search: bool = Field(
        default=True,
        description="Whether to enable file search tool",
    )
    vector_store_name: str = Field(
        default="product-docs",
        description="Vector store name for file search",
    )

    # Response settings
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Model temperature for responses",
    )
    max_tokens: Optional[int] = Field(
        default=4000,
        description="Maximum tokens in response",
    )

    # Tool settings
    enable_code_interpreter: bool = Field(
        default=False,
        description="Enable code interpreter tool",
    )
    custom_tools: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Custom function tools",
    )

    # Azure OpenAI settings (for image processing)
    azure_openai_endpoint: Optional[str] = Field(
        default=None,
        description="Azure OpenAI endpoint for image description",
    )
    azure_openai_api_key: Optional[str] = Field(
        default=None,
        description="Azure OpenAI API key",
    )

    class Config:
        """Pydantic config."""

        validate_assignment = True
