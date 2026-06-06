# LangChain Cheatsheet

## Installation

```bash
pip install langchain langchain-community langchain-openai
# For AWS Bedrock
pip install langchain-aws
# For Azure
pip install langchain-openai
```

## LLM Setup

### AWS Bedrock

```python
from langchain_aws import ChatBedrock

llm = ChatBedrock(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name="us-east-1"
)
```

### Azure OpenAI

```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_deployment="gpt-4",
    api_version="2024-02-15-preview"
)
```

## Basic Usage

### Simple Invocation

```python
from langchain_core.messages import HumanMessage

response = llm.invoke([HumanMessage(content="Hello!")])
print(response.content)
```

### With Prompts

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}")
])

chain = prompt | llm
response = chain.invoke({"input": "Hello!"})
```

## Chains (LCEL)

### Simple Chain

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"input": "Hello"})
```

### Multiple Steps

```python
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

## RAG

### Vector Store Setup

```python
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings

embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1")
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever()
```

### RAG Chain

```python
from langchain_core.runnables import RunnablePassthrough

rag_prompt = ChatPromptTemplate.from_template("""
Answer based on context:
{context}

Question: {question}
""")

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)
```

## Tools & Agents

### Define Tool

```python
from langchain_core.tools import tool

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"
```

### Create Agent

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor

tools = [search]
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
result = executor.invoke({"input": "Search for AI news"})
```

## Memory

### Conversation Memory

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(return_messages=True)
```

### With History

```python
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)
```

## Document Loading

```python
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    WebBaseLoader
)

# PDF
loader = PyPDFLoader("document.pdf")
docs = loader.load()

# Text splitting
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = splitter.split_documents(docs)
```

## Useful Links

- [LangChain Docs](https://python.langchain.com/)
- [LCEL Guide](https://python.langchain.com/docs/expression_language/)
- [LangChain Hub](https://smith.langchain.com/hub)
