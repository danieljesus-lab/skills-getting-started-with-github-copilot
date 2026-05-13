"""
Pytest configuration and shared fixtures for activity tests.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def fresh_activities():
    """
    Provide a fresh copy of the activities database for each test.
    This ensures test isolation and prevents state leakage between tests.
    """
    return copy.deepcopy(activities)


@pytest.fixture
def client(fresh_activities, monkeypatch):
    """
    Provide a TestClient with a fresh activities database for each test.
    Uses monkeypatch to replace the app's activities module with a fresh copy.
    """
    # Monkeypatch the activities dictionary in the app module
    monkeypatch.setattr("src.app.activities", fresh_activities)
    return TestClient(app)
