"""
Test suite for Mergington High School Activities API.
Tests follow the AAA (Arrange-Act-Assert) pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_success(self, client: TestClient):
        """
        Test that GET /activities returns a successful response.
        
        AAA Pattern:
        - ARRANGE: No setup required
        - ACT: Send GET request to /activities endpoint
        - ASSERT: Verify status code is 200
        """
        # ARRANGE
        # No additional setup needed, activities are pre-initialized in app.py
        
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client: TestClient):
        """
        Test that GET /activities returns all activities with correct structure.
        
        AAA Pattern:
        - ARRANGE: Define expected activities
        - ACT: Send GET request and parse response
        - ASSERT: Verify response contains all activities with correct keys
        """
        # ARRANGE
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Soccer Club", "Art Club", "Drama Club", "Debate Club", "Science Club"
        }
        
        # ACT
        response = client.get("/activities")
        activities_data = response.json()
        
        # ASSERT
        assert len(activities_data) == 9
        actual_names = set(activities_data.keys())
        assert actual_names == expected_activities

    def test_get_activities_has_correct_structure(self, client: TestClient):
        """
        Test that each activity has the required fields.
        
        AAA Pattern:
        - ARRANGE: Define expected fields
        - ACT: Fetch activities and check structure
        - ASSERT: Verify all required fields are present
        """
        # ARRANGE
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # ACT
        response = client.get("/activities")
        activities_data = response.json()
        
        # ASSERT
        for activity_name, activity_info in activities_data.items():
            assert isinstance(activity_info, dict)
            assert required_fields.issubset(set(activity_info.keys()))
            assert isinstance(activity_info["participants"], list)
            assert isinstance(activity_info["max_participants"], int)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup_for_activity(self, client: TestClient):
        """
        Test successful student signup for an activity.
        
        AAA Pattern:
        - ARRANGE: Define activity name and student email
        - ACT: Send POST request to signup endpoint
        - ASSERT: Verify status 200 and success message
        """
        # ARRANGE
        activity_name = "Basketball Team"
        student_email = "student@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert student_email in response.json()["message"]

    def test_signup_adds_student_to_participants_list(self, client: TestClient):
        """
        Test that signup successfully adds student to activity's participants.
        
        AAA Pattern:
        - ARRANGE: Get activities before signup
        - ACT: Sign up student and fetch updated activities
        - ASSERT: Verify student is in participants list
        """
        # ARRANGE
        activity_name = "Soccer Club"
        student_email = "newstudent@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity_name]["participants"].copy()
        
        # ACT
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Fetch updated activities
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[activity_name]["participants"]
        
        # ASSERT
        assert signup_response.status_code == 200
        assert student_email not in initial_participants
        assert student_email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1

    def test_signup_to_nonexistent_activity_returns_404(self, client: TestClient):
        """
        Test that signing up for non-existent activity returns 404 error.
        
        AAA Pattern:
        - ARRANGE: Define non-existent activity name and student email
        - ACT: Send POST request to non-existent activity
        - ASSERT: Verify 404 status and error message
        """
        # ARRANGE
        nonexistent_activity = "Nonexistent Club"
        student_email = "student@mergington.edu"
        
        # ACT
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": student_email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""

    def test_successful_unregister_from_activity(self, client: TestClient):
        """
        Test successful student unregistration from an activity.
        
        AAA Pattern:
        - ARRANGE: First signup a student, then prepare for unregister
        - ACT: Send DELETE request to unregister
        - ASSERT: Verify status 200 and success message
        """
        # ARRANGE
        activity_name = "Art Club"
        student_email = "artist@mergington.edu"
        
        # First, sign up the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # ACT
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # ASSERT
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert student_email in response.json()["message"]

    def test_unregister_removes_student_from_participants(self, client: TestClient):
        """
        Test that unregister successfully removes student from participants list.
        
        AAA Pattern:
        - ARRANGE: Signup student, verify they're in the list
        - ACT: Unregister student and fetch updated activities
        - ASSERT: Verify student is no longer in participants list
        """
        # ARRANGE
        activity_name = "Drama Club"
        student_email = "actor@mergington.edu"
        
        # First, sign up the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Verify student is in list
        before = client.get("/activities").json()[activity_name]["participants"]
        assert student_email in before
        
        # ACT
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Fetch updated activities
        after = client.get("/activities").json()[activity_name]["participants"]
        
        # ASSERT
        assert unregister_response.status_code == 200
        assert student_email not in after
        assert len(after) == len(before) - 1

    def test_unregister_from_nonexistent_activity_returns_404(self, client: TestClient):
        """
        Test that unregistering from non-existent activity returns 404 error.
        
        AAA Pattern:
        - ARRANGE: Define non-existent activity and student email
        - ACT: Send DELETE request to non-existent activity
        - ASSERT: Verify 404 status and error message
        """
        # ARRANGE
        nonexistent_activity = "Nonexistent Club"
        student_email = "student@mergington.edu"
        
        # ACT
        response = client.delete(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": student_email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
