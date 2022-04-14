import pytest
from flask import template_rendered
from server.main import create_app

# This file holds the test setup for existing API routes

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def test_client():
    flask_app = create_app()
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })
 
    testing_client = flask_app.test_client()
 
    ctx = flask_app.app_context()
    ctx.push()
    
    yield testing_client
 
    ctx.pop()

@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)
