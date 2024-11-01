import logging
import json


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record),
            "app": "fastapi",
        }
        return json.dumps(log_record)


def setup_logger():
    logger = logging.getLogger("app_logger")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    # Configure Uvicorn’s access and error loggers to use JSONFormatter
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = [handler]

    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers = [handler]

    return logger


app_logger = setup_logger()
