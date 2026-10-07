# AI Agent Workflow

A Python-based AI agent system that progressively evolved from basic tool calling into a stateful, goal-driven workflow capable of planning and executing multi-step tasks with verification.

## Current Capabilities

- Tool-based agent execution
- File creation, reading, listing, and searching
- Workspace and existing-file protection
- Persistent memory with `remember` and `recall`
- Semantic document search using embeddings
- Document chunking
- Persistent vector storage
- RAG-based context construction
- Knowledge retrieval through tool routing
- Multi-step task planning
- Plan-step evaluation
- Goal evaluation
- Agent state tracking
- Explicit verification of completed actions

## Architecture

```text
User Goal
   |
   v
Planner
   |
   v
Agent State
   |
   v
Agent Loop
   |
   +----> Tool Selection
   |          |
   |          v
   |      Tool Execution
   |          |
   |          v
   |      Plan Evaluation
   |          |
   |          v
   |      Goal Evaluation
   |
   +----> Memory / Knowledge / RAG
   |
   v
Verified Result