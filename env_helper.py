from pathlib import Path
import os

from dotenv import dotenv_values


def find_env_path() -> Path:
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).with_name(".env"),
        Path(__file__).parent / "1-BasicChatbot" / "1-BasicChatbot" / ".env",
    ]
    for path in candidates:
        if path.exists():
            return path
    msg = "Could not find .env. Expected it at project root or 1-BasicChatbot/1-BasicChatbot/.env"
    raise FileNotFoundError(msg)


def load_project_env() -> dict[str, str]:
    values = {k: v for k, v in dotenv_values(find_env_path()).items() if v}
    os.environ.update(values)
    return values

