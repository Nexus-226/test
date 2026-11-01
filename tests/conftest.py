"""Shared pytest fixtures for the Flask application."""

from importlib import import_module

import pytest


@pytest.fixture
def app():
    """Load the Flask app using the entry point required by README.md."""
    try:
        module = import_module("backend.app")
    except ModuleNotFoundError as exc:
        if exc.name in {"backend", "backend.app"}:
            pytest.fail(
                "backend/app.py is missing. Merge or copy the backend implementation "
                "before running the contract tests.",
                pytrace=False,
            )
        raise

    flask_app = getattr(module, "app", None)
    if flask_app is None:
        create_app = getattr(module, "create_app", None)
        if create_app is None:
            pytest.fail(
                "backend.app must expose either `app` or `create_app`, as required "
                "by `python -m flask --app backend.app run`.",
                pytrace=False,
            )
        flask_app = create_app()

    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    """Return Flask's in-process HTTP client."""
    return app.test_client()
