import os


WORKSPACE = "workspace"


def read_file(filename):

    workspace_path = os.path.abspath(WORKSPACE)

    file_path = os.path.abspath(
        os.path.join(WORKSPACE, filename)
    )

    if not file_path.startswith(workspace_path + os.sep):
        return "Error: Access outside workspace is not allowed."

    if not os.path.exists(file_path):
        return f"File not found: {filename}"

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
    
def list_files():

    files = []

    for filename in os.listdir(WORKSPACE):

        path = os.path.join(WORKSPACE, filename)

        if os.path.isfile(path):
            files.append(filename)

    return files

def search_files(query):
    results = []
    
    for filename in list_files():
        path = os.path.join(WORKSPACE, filename)
        
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
            
        if query.lower() in content.lower():
            results.append(filename)
            
    return results

def write_file(filename, content):
    """
    Write content to a new file inside the workspace.
    Refuses to overwrite an existing file.
    """

    workspace = os.path.abspath("workspace")

    file_path = os.path.abspath(
        os.path.join(workspace, filename)
    )

    # Security check
    if not file_path.startswith(workspace + os.sep):
        return "Error: Access outside workspace is not allowed."

    # Prevent accidental overwrite
    if os.path.exists(file_path):
        return f"Error: File '{filename}' already exists. Refusing to overwrite it."

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"File '{filename}' written successfully."

    except Exception as e:
        return f"Error writing file: {str(e)}"