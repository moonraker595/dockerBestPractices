from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_icat_doiminter():
    # Send a GET request to the /icat/doiminter endpoint
    response = client.get("/icat/doiminter")

    # Check if the status code is 200
    assert response.status_code == 200
