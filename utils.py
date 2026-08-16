from openai import OpenAI
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = ROOT_DIR / "files"
FILES_DIR.mkdir(parents=True, exist_ok=True)

client = OpenAI()


def get_text_gen_models():
    try:
        response = client.models.list()

        text_models = [
            m.id for m in response
            if m.id.startswith(("gpt-", "o1", "o3"))
        ]
        return sorted(text_models)
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []


def _get_files_path(filename: str) -> Path:
    path = Path(filename)
    if path.is_absolute() or len(path.parts) != 1 or path.name in {"", ".", ".."}:
        raise ValueError(
            "filename must be a file name without directory components"
        )
    return FILES_DIR / path.name