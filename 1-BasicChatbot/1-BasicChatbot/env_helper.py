from pathlib import Path
import os

from dotenv import dotenv_values


ENV_PATH = Path(__file__).with_name(".env")


def load_project_env() -> dict[str, str]:
    values = {k: v for k, v in dotenv_values(ENV_PATH).items() if v}
    os.environ.update(values)
    return values

