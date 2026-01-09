# Agent Architectures

Common patterns for building AI agents.

## ReAct Pattern

Reasoning and Acting in an interleaved manner.

```
Thought: I need to find information about X
Action: search("X")
Observation: [search results]
Thought: Based on the results, I should...
Action: [next action]
...
Final Answer: [response]
```

### Implementation

```python
REACT_PROMPT = """
Answer the question using the available tools.

Tools: {tools}

Use this format:
Thought: [reasoning]
Action: [tool_name]
Action Input: [input]
Observation: [result]
... (repeat as needed)
Thought: I have enough information
Final Answer: [answer]

Question: {question}
"""
```

## Plan-and-Execute

Create a plan first, then execute steps.

```
Plan:
1. Search for X
2. Analyze results
3. Summarize findings

Execution:
Step 1: [execute and observe]
Step 2: [execute and observe]
Step 3: [execute and observe]

Result: [final output]
```

### Implementation

```python
# Planner creates the plan
plan = planner.invoke({"objective": task})

# Executor runs each step
for step in plan.steps:
    result = executor.invoke({"step": step, "context": context})
    context.update(result)
```

## Multi-Agent Systems

### Supervisor Pattern

One agent coordinates multiple specialist agents.

```
        [Supervisor]
       /     |      \
  [Agent1] [Agent2] [Agent3]
  (Search) (Analyze) (Write)
```

### Debate Pattern

Multiple agents discuss and refine.

```
Agent A: [Initial response]
Agent B: [Critique/Alternative]
Agent A: [Refined response]
Arbiter: [Final decision]
```

## Tool Selection

### Static Tools

```python
tools = [search_tool, calculator_tool, database_tool]
agent = create_agent(llm, tools)
```

### Dynamic Tool Loading

```python
def get_tools_for_task(task_type):
    if task_type == "research":
        return [search_tool, web_scraper]
    elif task_type == "data":
        return [database_tool, calculator]
    return default_tools
```

## Memory Patterns

### Short-term (Conversation)

```python
memory = ConversationBufferMemory()
# Stores recent messages
```

### Long-term (Persistent)

```python
# Store in vector DB
long_term = VectorStoreRetriever(vectorstore)
# Retrieve relevant past interactions
```

### Working Memory

```python
# Scratchpad for current task
working_memory = {
    "current_task": task,
    "gathered_info": [],
    "intermediate_results": []
}
```

## Error Handling

### Retry with Feedback

```python
for attempt in range(max_retries):
    try:
        result = agent.invoke(task)
        if validate(result):
            return result
        task = f"{task}\n\nPrevious attempt failed: {feedback}"
    except Exception as e:
        task = f"{task}\n\nError occurred: {e}"
```

### Graceful Degradation

```python
try:
    result = primary_agent.invoke(task)
except:
    result = fallback_agent.invoke(simplified_task)
```

## Best Practices

1. **Clear tool descriptions**: Help the agent choose correctly
2. **Bounded iterations**: Set max steps to prevent infinite loops
3. **Observation limits**: Truncate long tool outputs
4. **Structured output**: Use Pydantic models for reliability
5. **Logging**: Track all agent decisions for debugging
