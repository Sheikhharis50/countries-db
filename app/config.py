# type: ignore

import dataclasses
import logging
import os
from pathlib import Path

import environ

from . import logger

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
# reading .env file
env.read_env(os.path.join(BASE_DIR, ".env"))


@dataclasses.dataclass
class Settings:
    # pylint: disable=invalid-name

    """
    App Settings
    """

    DEBUG: bool
    SECRET_KEY: str
    BASE_DIR: Path
    DATA_DIR: Path = dataclasses.field(init=False)
    API_URL: str
    LOGGING_LEVEL: str

    def __post_init__(self):
        self.DATA_DIR = self.BASE_DIR / "data"
        self.make_data_dir()

    def make_data_dir(self):
        """Make data directory"""
        if os.path.exists(self.DATA_DIR):
            return

        try:
            os.mkdir(self.DATA_DIR)
        except OSError as e:
            logger.error(e)


settings = Settings(
    DEBUG=env("DEBUG", default=True),
    SECRET_KEY=env("SECRET_KEY"),
    BASE_DIR=BASE_DIR,
    API_URL=env("API_URL", default="http://localhost:8000"),
    LOGGING_LEVEL=env("LOGGING_LEVEL", default="INFO"),
)

logging.basicConfig(
    level=getattr(logging, settings.LOGGING_LEVEL),
    format=(
        "[%(asctime)s][%(levelname)s]"
        "[PID:%(process)d][Thread:%(thread)d]"
        "[%(name)s][%(funcName)s:%(lineno)s][%(message)s]"
    ),
)
