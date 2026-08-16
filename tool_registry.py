import sys
import importlib
import inspect
from pathlib import Path
import importlib.util
from types import ModuleType
from dataclasses import dataclass
from agents import Agent, RunContextWrapper, FunctionTool
import logging

logger = logging.getLogger("tool_registry")

TOOL_REGISTRY = {}


def import_modules_from_directory(base_dir: str, package_prefix: str):
    """
    Recursively import all .py modules in a given directory and prefix.
    """
    logger.info(f"Importing modules from {base_dir}")

    base_path = Path(base_dir).resolve()

    for py_file in base_path.rglob("*.py"):
        if py_file.name.startswith("_"):
            continue  # skip __init__.py, etc.

        relative_path = py_file.relative_to(base_path)
        module_parts = [package_prefix] + list(relative_path.with_suffix("").parts)
        module_name =".".join(module_parts)

        try:
            logger.info(f"Importing module: {module_name}")
            importlib.import_module(module_name)
        except Exception as e:
            logger.error(f"[WARN] Could not import {module_name}: {e}")


def build_registries(search_path="tools"):
    """
    Build HANDOFF_HANDLER_REGISTRY, DATA_MODEL_REGISTRY, and TOOL_REGISTRY by scanning the agent_components/ directory.
    Maps Agent subclasses for agents that have modified on_message functions.
    """
    logger.info(f"Starting registry building for modules in {search_path}")

    global TOOL_REGISTRY

    TOOL_REGISTRY.clear()

    import_modules_from_directory(search_path, package_prefix=search_path.replace("/", ""))
    try:
        for mod in list(sys.modules.values()):
            if not isinstance(mod, ModuleType) or not mod.__name__.startswith(search_path.replace("/", ".")):
                continue

            for name, obj in inspect.getmembers(mod):
                if isinstance(obj, FunctionTool):
                    TOOL_REGISTRY[name] = obj

        logger.info(f"Registered Tools: {list(TOOL_REGISTRY.keys())}")
        logger.info(f"Finished registry building for modules in {search_path}")

    except Exception as e:
        logger.error(f"Error occurred during registry scanning:\n{e}")
        raise e


