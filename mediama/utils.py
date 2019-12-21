from pathlib import Path

def get_project_root():
    """
    Get the path of the project root directory
    :returns: project root dir
    """
    return Path(__file__).parent.parent
