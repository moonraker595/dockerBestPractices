from api.logger import app_logger
from fastapi import FastAPI
from api.icat_queries import icatQueries
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from api.config import settings

# By default, sets up OpenAPI documentation for the APP at /docs
app = FastAPI(
    title="ICAT API",
    description="An example API for querying user information from the ICAT server",
    version=settings.version,
    contact={
        "name": "Alexander Kemp",
    }
)

app_logger.info("Application started")

# Define a global counter for endpoint hits
endpoint_hits_counter = Counter('endpoint_hits', 'Count of hits on the /icat endpoint')


@app.get("/icat/{username}", summary="Get user information",
         description="Returns user information from the ICAT server")
async def get_user(username: str):
    endpoint_hits_counter.inc()
    app_logger.info("endpoint hit")
    # login to ICAT
    icatQueries.login()
    # get the user from icat
    user = icatQueries.get("User", "name", username)
    # return user info
    return user.instance


@app.get("/metrics", summary="Get metrics", description="Returns Prometheus metrics for the application")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.get("/version", summary="Get API version", description="Returns the current version of the API")
async def version():
    return {"version": settings.version}
