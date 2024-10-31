from api.logger import app_logger
from fastapi import FastAPI
from api.icat_queries import icatQueries

app = FastAPI()
app_logger.info("Application started")
hit_counter = {"endpoint_hits": 0}


@app.get("/icat/{username}")
async def get_user(username: str):
    hit_counter["endpoint_hits"] += 1
    app_logger.info("Get user endpoint hit")
    # login to ICAT
    icatQueries.login()
    # get the user from icat
    user = icatQueries.get("User", "name", username)
    return user.instance


@app.get("/metrics")
def metrics():
    return hit_counter
