import logging
import logging.config
from pathlib import Path



def setup_logging(log_file_path: str = ""):
    if len(log_file_path) == 0:
        log_file_path += f"{project_name}.log"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"standard": {"format": "%(asctime)s - %(name)s - %(levelname)-8s - %(message)s"}},
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "formatter": "standard",
                "filename": log_file_path,
                "mode": "a",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    }

    logging.config.dictConfig(logging_config)


project_name = Path().absolute().parent.name
logger = logging.getLogger(project_name)
