# AI Agent Workflow

A local, tool-using AI agent built in Python and powered by Ollama.

This project started as a basic tool-calling experiment and evolved into a stateful multi-step agent that can understand a user goal, create an ordered execution plan, select and execute tools, track execution state, evaluate plan progress, evaluate overall goal completion, work with a protected workspace, store and recall persistent memory, search documents semantically, retrieve grounded context through RAG, and verify requested work.

The current entry point is **agent_v10.py**.

> **Current milestone:** planning + state tracking + tool execution + plan-step evaluation + goal evaluation + verification, with memory and RAG foundations.

## Table of Contents

- [What this project does](#what-this-project-does)
- [Architecture](#architecture)
- [How a request is executed](#how-a-request-is-executed)
- [Features](#features)
- [Tools](#tools)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run the agent](#run-the-agent)
- [Prepare semantic search / RAG](#prepare-semantic-search--rag)
- [Example tasks](#example-tasks)
- [Understanding the output](#understanding-the-output)
- [How the main modules work](#how-the-main-modules-work)
- [Generated files](#generated-files)
- [Troubleshooting](#troubleshooting)
- [Current limitations](#current-limitations)
- [Development roadmap](#development-roadmap)

## What this project does

This is not just a chatbot that generates text. The agent is designed around an execution loop.

For example, given:

> Read ml_notes.txt, create ml_summary.txt using the notes, and verify that the file was created.

The agent creates a plan:

1. Read ml_notes.txt
2. Create ml_summary.txt
3. Verify that ml_summary.txt was created successfully

It then executes the required tools one step at a time.

After every successful tool call, the system evaluates whether the current plan step was actually completed. The overall goal is only considered complete when all planned steps have been satisfied.

This prevents the agent from simply saying that something was done when the corresponding tool operation never succeeded.

## Architecture

~~~text
                         User Goal
                            |
                            v
                     +--------------+
                     |    Planner   |
                     +--------------+
                            |
                            v
                     +--------------+
                     |  AgentState  |
                     +--------------+
                            |
                            v
                  +---------------------+
                  |    Agent Loop       |
                  |                     |
                  |  Select Tool        |
                  |       |             |
                  |       v             |
                  |  Execute Tool       |
                  |       |             |
                  |       v             |
                  | Plan-Step Evaluator |
                  |       |             |
                  |       v             |
                  |  Goal Evaluator     |
                  +---------------------+
                     |             |
                     |             |
                     v             v
                Memory / RAG    File Tools
                     |             |
                     v             v
                Semantic Search  Workspace
                     |
                     v
                Verified Result
~~~

### Main execution loop

~~~text
User goal
   ↓
Create plan
   ↓
Initialize AgentState
   ↓
Select current plan step
   ↓
LLM chooses an appropriate tool
   ↓
Execute tool
   ↓
Record result in AgentState
   ↓
Evaluate current plan step
   ↓
Evaluate overall goal
   ├── CONTINUE → execute remaining work
   ├── COMPLETE → produce final response
   └── FAILED   → stop and report failure
~~~

## How a request is executed

### 1. Planning

planner.py asks the local LLM to convert the user's goal into a small ordered list of steps.

The planner is instructed to:

- return JSON
- preserve filenames supplied by the user
- keep steps ordered
- include verification when required
- avoid unnecessary steps
- plan only, without executing tools

### 2. State tracking

agent_state.py maintains the state of the current task.

It tracks:

- original goal
- execution plan
- completed plan steps
- current plan step
- agent status
- loop iterations
- total tool calls
- successful tool calls
- failed tool calls
- tool execution history

### 3. Tool selection and execution

The LLM receives the available tool schemas and chooses the appropriate tool.

The project currently supports tools for:

- arithmetic
- persistent memory
- file operations
- keyword file search
- semantic search
- knowledge retrieval
- file creation

### 4. Plan-step evaluation

plan_evaluator.py checks whether the tool result satisfies the current plan step.

For example:

~~~text
Plan step:
Read ml_notes.txt

Tool:
read_file

Arguments:
{"filename": "ml_notes.txt"}

Result:
<file contents>

→ COMPLETED
~~~

If the wrong file is read, the plan step is not marked complete.

### 5. Goal evaluation

goal_evaluator.py determines whether the agent should:

- CONTINUE
- COMPLETE
- FAILED

A failed tool operation takes priority over completion.

When a plan exists, the overall goal is considered complete only after every planned step has been completed.

### 6. Verification

Verification is treated as an actual tool operation.

For example, after creating a file, a verification step can read or list the file rather than relying on the model's claim that the file exists.

## Features

### Tool calling

The agent uses Ollama's tool-calling interface to select functions from a registered tool set.

### Protected workspace

File operations are restricted to the workspace/ directory.

The file tools reject paths that attempt to escape the workspace.

### Existing-file protection

write_file refuses to overwrite an existing file.

This prevents an agent action from silently replacing an existing workspace document.

### Persistent memory

memory.py provides:

- remember
- recall

Memory is stored locally in memory.json.

Memory retrieval uses embeddings and cosine similarity rather than simple keyword matching.

### Semantic document search

The project contains multiple stages of retrieval development:

1. whole-document semantic search
2. document chunking
3. chunk-level semantic search
4. persistent vector indexing
5. persistent semantic retrieval
6. RAG context construction
7. knowledge-tool routing

### RAG

rag.py converts retrieved document chunks into context for the language model.

The RAG prompt explicitly instructs the model to:

- use retrieved context as the primary source of truth
- avoid unsupported facts
- state when the context is insufficient
- mention source filenames when useful

## Tools

The current tool registry is defined in tools.py.

| Tool | Purpose |
|---|---|
| add | Add two numbers |
| multiply | Multiply two numbers |
| divide | Divide two numbers |
| calculator | Evaluate basic arithmetic expressions |
| remember | Store information in persistent memory |
| recall | Retrieve relevant stored memories |
| read_file | Read a workspace file |
| list_files | List workspace files |
| search_files | Search file contents by text |
| semantic_search | Search workspace files by semantic similarity |
| search_knowledge | Retrieve relevant indexed document chunks |
| write_file | Create a new workspace file |

## Project structure

~~~text
AI-Agent-Workflow/
│
├── agent_v10.py          # Main agent application / execution loop
├── agent_state.py        # Runtime state and tool history
│
├── planner.py            # Natural-language goal → ordered plan
├── plan_evaluator.py     # Evaluates individual plan steps
├── goal_evaluator.py     # Evaluates overall task status
│
├── tools.py              # Tool registry and LLM tool schemas
├── calculator.py         # Safe basic arithmetic evaluator
├── file_tools.py         # Workspace file operations
│
├── memory.py             # Persistent semantic memory
├── knowledge_tools.py    # Knowledge retrieval tool
│
├── document_search.py    # Whole-document semantic search
├── chunking.py           # Text chunking
├── chunk_search.py       # Chunk-level semantic search
├── vector_store.py       # Persistent vector index creation/loading
├── persistent_search.py  # Search over persistent vector index
├── rag.py                # RAG context and prompt construction
│
├── workspace/             # Example/user documents used by the agent
│   ├── ml_notes.txt
│   ├── ml_summary_v6.txt
│   └── python_notes.txt
│
├── .gitignore
└── README.md
~~~

## Requirements

You need:

- Python
- Git
- Ollama

The Python code uses the Ollama Python package and otherwise relies on Python's standard library for the current implementation.

### Local Ollama models

The current code expects these exact model names:

| Model | Used for |
|---|---|
| qwen3:4b | Agent responses and planning |
| nomic-embed-text | Embeddings for memory and document retrieval |

The model names are hard-coded in the current implementation, so changing the model requires updating the corresponding Python files.

## Installation

### 1. Clone the repository

~~~bash
git clone https://github.com/SubhamDey2004-coder/AI-Agent-Workflow.git
cd AI-Agent-Workflow
~~~

Run the agent from the repository root because the file tools expect the workspace/ directory relative to the current working directory.

### 2. Create a virtual environment

#### Windows PowerShell

~~~powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
~~~

#### macOS / Linux

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

### 3. Install the Python dependency

~~~bash
pip install ollama
~~~

### 4. Install Ollama

Install Ollama from:

https://ollama.com/download

On Windows, Ollama can also be installed from PowerShell using the official installer command:

~~~powershell
irm https://ollama.com/install.ps1 | iex
~~~

### 5. Download the required models

~~~bash
ollama pull qwen3:4b
ollama pull nomic-embed-text
~~~

Verify:

~~~bash
ollama list
~~~

You should see both required models.

## Run the agent

From the repository root, with the virtual environment activated:

~~~bash
python agent_v10.py
~~~

You should see:

~~~text
Agent started. Type 'exit' to stop.

You:
~~~

Enter a task.

To stop the program:

~~~text
exit
~~~

## Prepare semantic search / RAG

The repository intentionally does not commit vector_index.json.

This keeps generated embeddings out of Git and allows each user to build an index from their own workspace.

After installing nomic-embed-text, build the index from the current workspace/ contents:

~~~bash
python -c "from vector_store import build_index; build_index(); print('Vector index built successfully.')"
~~~

This creates:

~~~text
vector_index.json
~~~

The file is ignored by Git.

### Important

If you add or modify documents in workspace/, rebuild the vector index before using persistent knowledge search again:

~~~bash
python -c "from vector_store import build_index; build_index(); print('Vector index rebuilt successfully.')"
~~~

Without an index, search_knowledge has no persistent document records to search.

## Example tasks

### Example 1: Simple calculation

~~~text
Calculate (25 * 4) + 17
~~~

The agent should select the calculator tool.

### Example 2: Read a file

~~~text
Read ml_notes.txt
~~~

The agent should use read_file.

### Example 3: Create and verify a file

~~~text
Read ml_notes.txt and create ml_summary_new.txt containing a concise summary. Then verify that ml_summary_new.txt was created successfully.
~~~

Expected high-level workflow:

~~~text
PLAN
  ↓
Read ml_notes.txt
  ↓
Write ml_summary_new.txt
  ↓
Read / verify ml_summary_new.txt
  ↓
Goal COMPLETE
~~~

Because write_file refuses to overwrite an existing file, choose a filename that does not already exist.

### Example 4: Use persistent knowledge

First build the vector index:

~~~bash
python -c "from vector_store import build_index; build_index()"
~~~

Then run the agent:

~~~bash
python agent_v10.py
~~~

Ask something related to the indexed notes, for example:

~~~text
What do my machine learning notes say about supervised learning?
~~~

The agent can route the request through search_knowledge, retrieve relevant chunks, construct RAG context, and use that context to answer.

### Example 5: Persistent memory

You can ask the agent to remember information:

~~~text
Remember that my preferred programming language is Python.
~~~

Later:

~~~text
What programming language did I ask you to remember?
~~~

Memory is stored locally in memory.json.

## Understanding the output

For a multi-step task, the console shows the agent's execution state.

A successful run looks conceptually like:

~~~text
========== PLAN ==========
1. Read ml_notes.txt
2. Create ml_summary_v6.txt using the contents of ml_notes.txt
3. Verify that ml_summary_v6.txt was created successfully
==========================

Agent selected tool: read_file
...

Plan step result: COMPLETED
Goal evaluator: CONTINUE

Agent selected tool: write_file
...

Plan step result: COMPLETED
Goal evaluator: CONTINUE

Agent selected tool: read_file
...

Plan step result: COMPLETED

Goal evaluator: COMPLETE
~~~

The final state reports:

- task status
- number of agent steps
- plan progress
- total tool calls
- successful tools
- failed tools
- tool history

## How the main modules work

### agent_v10.py

The main runtime.

It:

1. receives the user goal
2. creates an AgentState
3. creates an execution plan
4. sends the plan to the model
5. executes one tool step at a time
6. records results
7. evaluates plan progress
8. evaluates the overall goal
9. constructs RAG context when knowledge retrieval is used
10. produces a final response only after completion

### planner.py

Converts a natural-language goal into ordered plan steps.

Example:

~~~text
Input:
Read A and create B, then verify B.

Output:
[
  "Read A",
  "Create B using the contents of A",
  "Verify that B was created successfully"
]
~~~

### agent_state.py

Provides the runtime state machine for a task.

It keeps the agent aware of what it planned, what it completed, what tools it called, and whether those tools succeeded.

### plan_evaluator.py

Checks whether the latest tool execution satisfies the current planned step.

This is intentionally separate from the LLM so that plan progress is not based solely on the model claiming that a step is complete.

### goal_evaluator.py

Provides the overall task decision:

~~~text
CONTINUE
COMPLETE
FAILED
~~~

### file_tools.py

Handles workspace operations and applies two important protections:

1. paths cannot escape the workspace
2. existing files cannot be overwritten by write_file

### memory.py

Stores memory locally and uses Ollama embeddings plus cosine similarity for retrieval.

### vector_store.py

Builds a persistent JSON vector index from chunked workspace documents.

### persistent_search.py

Loads that index and performs cosine-similarity retrieval.

### rag.py

Turns retrieved chunks into a grounded context and prompt for the language model.

## Generated files

The following files are deliberately not committed:

| File | Reason |
|---|---|
| .venv/ | Local Python environment |
| __pycache__/ | Python-generated cache |
| memory.json | Local persistent memory |
| vector_index.json | Generated embedding index |
| experimental agent versions | Historical development files |
| temporary workspace experiments | Local development artifacts |

This means a fresh clone starts clean. Generated state is created locally when needed.

## Troubleshooting

### ModuleNotFoundError: No module named 'ollama'

Activate your virtual environment and install the Python package:

~~~bash
pip install ollama
~~~

### model qwen3:4b not found

Pull the required model:

~~~bash
ollama pull qwen3:4b
~~~

### model nomic-embed-text not found

Pull the embedding model:

~~~bash
ollama pull nomic-embed-text
~~~

### Ollama connection errors

Make sure Ollama is installed and running, then check:

~~~bash
ollama list
~~~

The Python client communicates with the local Ollama service.

### Knowledge search returns no results

Build the persistent index:

~~~bash
python -c "from vector_store import build_index; build_index(); print('Vector index built successfully.')"
~~~

Also make sure the relevant document is inside workspace/.

### Error: File already exists

This is intentional.

write_file refuses to overwrite existing files. Use a new filename or remove the old local test file manually if you no longer need it.

### File not found

Make sure:

- you are running the program from the repository root
- the requested file exists inside workspace/
- the filename matches exactly

## Current limitations

This repository represents an active development milestone rather than a production-ready autonomous agent.

Current limitations include:

- command-line interface only
- local Ollama dependency
- model names are currently hard-coded
- generated vector indexes must be rebuilt when source documents change
- plan-step evaluation currently uses rule-based checks for supported step types
- failure recovery and automatic replanning are not yet implemented
- no FastAPI/web interface is included in this milestone
- no automated test suite is included yet
- no production deployment configuration is included yet

These limitations are intentional parts of the project's current development stage.

## Development roadmap

The next development stages are planned around making the agent more reliable and production-oriented:

1. **Structured planning**
   - machine-readable actions
   - explicit targets
   - explicit completion conditions

2. **Deterministic execution**
   - stronger separation between planning and execution
   - tighter action validation

3. **Failure recovery**
   - retry strategies
   - failure classification
   - automatic replanning

4. **Stronger verification**
   - output validation
   - content validation
   - task-specific verification conditions

5. **Advanced memory and retrieval**
   - improved memory management
   - better retrieval quality
   - richer document ingestion

6. **Application layer**
   - FastAPI backend
   - API endpoints
   - user-facing interface

7. **Productionization**
   - logging
   - testing
   - containerization
   - deployment
   - monitoring

## Why this project exists

The purpose of this project is to understand how an AI agent moves beyond a single LLM response.

The central idea is:

~~~text
LLM response
     ↓
Tool calling
     ↓
State
     ↓
Planning
     ↓
Execution
     ↓
Verification
     ↓
Reliable task completion
~~~

The project is therefore being developed incrementally, with each milestone adding another layer of control around the language model.

## License

No license has been added to this repository yet.
