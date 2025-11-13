from factorio_web import app, static_file
from litestar.testing import TestClient


def test_app_dir() -> None:
    """terrible test that basically just checks that the app object exists"""
    assert "route_map" in dir(app)


def test_static_file() -> None:
    """test static file handler with a known file"""

    client = TestClient(app)
    response = client.get("/static/script.js")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/javascript"
    assert "function" in response.text  # crude check that it's JS content
