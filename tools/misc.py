from pathlib import Path
from agents import function_tool
from typing import List
from datetime import datetime
import logging

from utils import FILES_DIR

logger = logging.getLogger(__name__)


@function_tool
def read_files_dir() -> List[str]:
    """Returns a list of files available to read."""
    return [
        f.name
        for f in FILES_DIR.iterdir()
        if f.is_file()
    ]


@function_tool
def get_current_date():
    """
    Returns the current date and time.

    Returns:
        str: Current date in ISO 8601 format (YYYY-MM-DD).
    """
    return datetime.now().date().isoformat()