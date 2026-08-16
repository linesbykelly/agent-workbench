import logging
from typing import Dict, List
from agents import function_tool
import pandas as pd

from utils import _get_files_path

logger = logging.getLogger(__name__)


@function_tool(strict_mode=False)
def read_csv(filename: str) -> Dict:
    """
    Reads a CSV file from the files directory.

    Args:
        filename: Name of the CSV file.

    Returns:
        Dict containing the CSV data.
    """
    try:
        file_path = _get_files_path(filename)

        df = pd.read_csv(file_path)

        logger.info(
            f"Successfully read {filename} with {len(df)} rows."
        )

        return {
            "success": True,
            "data": df.to_json(orient="records"),
            "error": None
        }

    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")

        return {
            "success": False,
            "data": None,
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        }


@function_tool(strict_mode=False)
def write_csv(data: List[Dict], filename: str) -> Dict:
    """
    Writes a CSV file to the files directory.

    Args:
        data: Data to write to the CSV.
        filename: Name of the CSV file.

    Returns:
        Dict containing the result of the operation.
    """
    try:
        file_path = _get_files_path(filename)

        df = pd.DataFrame.from_records(data)
        df.to_csv(file_path, index=False)

        logger.info(
            f"Successfully wrote {filename} with {len(df)} rows."
        )

        return {
            "success": True,
            "data": f"Successfully wrote CSV: {filename}",
            "error": None
        }

    except Exception as e:
        logger.error(f"Failed to write CSV: {e}")

        return {
            "success": False,
            "data": None,
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        }


@function_tool(strict_mode=False)
def write_text_file(
    filename: str,
    contents: str,
    mode: str = "w"
) -> Dict:
    """
    Writes a text file to the files directory.

    Args:
        filename: Name of the text file.
        contents: Text content to write.
        mode: 'w' to overwrite or 'a' to append.

    Returns:
        Dict containing the result of the operation.
    """
    try:
        if mode not in ["a", "w"]:
            raise ValueError(
                "Invalid mode. Must be 'w' or 'a'."
            )

        if not filename.endswith(".txt"):
            raise ValueError(
                "Filename must end with '.txt'."
            )

        file_path = _get_files_path(filename)

        with open(
            file_path,
            encoding="utf-8",
            mode=mode
        ) as f:
            f.write(contents)

        return {
            "success": True,
            "data": f"Successfully wrote text file: {filename}",
            "error": None
        }

    except Exception as e:
        logger.error(f"Failed to write text file: {e}")

        return {
            "success": False,
            "data": None,
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        }


@function_tool(strict_mode=False)
def read_text_file(filename: str) -> Dict:
    """
    Reads a text file from the files directory.

    Args:
        filename: Name of the text file.

    Returns:
        Dict containing the file contents.
    """
    try:
        file_path = _get_files_path(filename)

        with open(
            file_path,
            encoding="utf-8",
            mode="r"
        ) as f:
            contents = f.read()

        return {
            "success": True,
            "data": contents,
            "error": None
        }

    except Exception as e:
        logger.error(f"Failed to read text file: {e}")

        return {
            "success": False,
            "data": None,
            "error": {
                "type": type(e).__name__,
                "message": str(e)
            }
        }