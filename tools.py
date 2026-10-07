from calculator import calculate
from memory import remember, recall
from file_tools import (
    read_file, list_files, search_files, write_file
)
from document_search import semantic_search
from knowledge_tools import search_knowledge


def add(a: int, b: int) -> int:
    return a + b


def multiply(a: int, b: int) -> int:
    return a * b


def divide(a: int, b: int) -> float:
    return a / b

def calculator(expression: str):
    return calculate(expression)

tool_registry = {
    "add": add,
    "multiply": multiply,
    "divide": divide,
    "calculator": calculator,
    "remember": remember,
    "recall": recall,
    "read_file": read_file,
    "list_files": list_files,
    "search_files": search_files,
    "semantic_search": semantic_search,
    "search_knowledge": search_knowledge,
    "write_file": write_file
}

def get_tool_schemas():
    return [
        {
            "type": "function",
            "function": {
                "name": "add",
                "description": "Add two numbers together.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "integer",
                            "description": "The first number."
                        },
                        "b": {
                            "type": "integer",
                            "description": "The second number."
                        }
                    },
                    "required": ["a", "b"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "multiply",
                "description": "Multiply two numbers together.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "integer",
                            "description": "The first number."
                        },
                        "b": {
                            "type": "integer",
                            "description": "The second number."
                        }
                    },
                    "required": ["a", "b"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "divide",
                "description": "Divide the first number by the second number.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {
                            "type": "integer",
                            "description": "The number to be divided."
                        },
                        "b": {
                            "type": "integer",
                            "description": "The number to divide by."
                        }
                    },
                    "required": ["a", "b"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Evaluate a mathematical expression using numbers and basic arithmetic operators (+, -, *, /).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "A mathematical expression such as '(25 * 4) + 17'."
                        }
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remember",
                "description": "Save an important piece of information to persistent memory for future conversations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The information that should be remembered."
                        }
                    },
                    "required": ["content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "recall",
                "description": "Search persistent memory for information related to a query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "A keyword or phrase to search for in memory."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a text file from the agent workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                        "type": "string",
                        "description": ("Read the complete contents of a specific file. "
                                        "Use this only when the user explicitly names a file "
                                        "or specifically asks to read/open a file."),
                        }
                    },
                    "required": ["filename"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": ("List the files available in the workspace. "
                                "Use this only when the user asks what files are available "
                                "or asks to list the workspace contents."),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Search the contents of files in the agent workspace and return filenames containing the query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The text or topic to search for inside workspace files."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "semantic_search",
                "description": "Search workspace files by semantic meaning and return the most relevant files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question or topic to search for semantically."
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_knowledge",
                "description": (
                    "Search the user's stored documents using semantic search. "
                    "Use this tool FIRST whenever the user asks a question about "
                    "information contained in their notes, documents, or workspace. "
                    "Do NOT use list_files or read_file just to find information "
                    "when semantic search can answer the question. "
                    "Use read_file only when the user explicitly asks to read a "
                    "specific file."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "The user's question or information need to search "
                                "for in stored documents."
                            )
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file inside the workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to create inside the workspace."
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write into the file."
                        }
                    },
                    "required": ["filename", "content"]
                }
            }
        }
    ]