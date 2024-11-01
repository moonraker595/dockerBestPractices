from api.logger import app_logger
from fastapi import FastAPI
from api.icat_queries import icatQueries
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from api.config import settings

app = FastAPI()
app_logger.info("Application started")

# Define a global counter for endpoint hits
endpoint_hits_counter = Counter('endpoint_hits', 'Count of hits on the /icat endpoint')


@app.get("/icat/{username}")
async def get_user(username: str):
    endpoint_hits_counter.inc()
    app_logger.info("Get user endpoint hit")
    # login to ICAT
    icatQueries.login()
    # get the user from icat
    user = icatQueries.get("User", "name", username)
    return user.instance


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/version")
async def version():
    return {"version": settings.version}
