import json
import os

from memory import get_embedding
from file_tools import list_files, read_file
from chunking import chunk_text

INDEX_FILE = "vector_index.json"

def build_index():
    records = []
    
    for filename in list_files():
        content = read_file(filename)
        
        if content.startswith("Error:") or content.startswith("File not found"):
            continue
        
        chunks = chunk_text(content)
        
        
        for index, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            records.append({
                "filename": filename,
                "chunk_index": index,
                "content": chunk,
                "embedding": embedding
            })
            
    with open(INDEX_FILE, "w", encoding="utf-8") as file:
        json.dump(records, file)
        
    return records

def load_index():
    if not os.path.exists(INDEX_FILE):
        return []
    
    with open(INDEX_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

