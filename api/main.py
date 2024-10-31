import logging
from fastapi import FastAPI
from api.icat_queries import icatQueries
import json

app = FastAPI()


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record),
            "module": record.module,
            "source": "fastapi"  # Add custom source field
        }
        return json.dumps(log_record)


# Apply the custom formatter
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("app_logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)


logger.info("starting")


@app.get("/icat/{username}")
async def say_hello(username: str):
    # login to ICAT
    icatQueries.login()
    # get the user from icat
    user = icatQueries.get("User", "name", username)
    logger.info(f"TEST")
    return user.instance
