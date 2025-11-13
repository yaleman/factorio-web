from factorio_web import app


def test_app_dir() -> None:
    """terrible test that basically just checks that the app object exists"""
    assert "route_map" in dir(app)
