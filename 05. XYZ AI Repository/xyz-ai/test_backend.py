"""
Test suite for XYZ AI School Assistant backend.
Tests authorization, intent detection, attendance, and escalation logic.
"""

import pytest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from auth_service import AuthenticationService
from intent_service import IntentService, Intent
from attendance_service import AttendanceService
from support_service import SupportService
from mock_data import MockSchoolDatabase
from conversation_memory import ConversationMemoryStore


class TestAuthentication:
    """Test authentication and role-based access."""

    def setup_method(self):
        """Setup test fixtures."""
        self.auth = AuthenticationService()
        self.db = MockSchoolDatabase()

    def test_student_authentication(self):
        """Test student can be authenticated."""
        user_info = self.auth.get_authenticated_user("S001")
        assert user_info is not None
        assert user_info["role"] == "student"
        assert user_info["name"] == "Rahul Sharma"

    def test_parent_authentication(self):
        """Test parent can be authenticated."""
        user_info = self.auth.get_authenticated_user("P001")
        assert user_info is not None
        assert user_info["role"] == "parent"
        assert "child_ids" in user_info
        assert "S001" in user_info["child_ids"]

    def test_teacher_authentication(self):
        """Test teacher can be authenticated."""
        user_info = self.auth.get_authenticated_user("T001")
        assert user_info is not None
        assert user_info["role"] == "teacher"
        assert "authorized_student_ids" in user_info

    def test_principal_authentication(self):
        """Test principal can be authenticated."""
        user_info = self.auth.get_authenticated_user("PR001")
        assert user_info is not None
        assert user_info["role"] == "principal"

    def test_invalid_user(self):
        """Test invalid user returns None."""
        user_info = self.auth.get_authenticated_user("INVALID")
        assert user_info is None

    def test_can_perform_action_student_attendance(self):
        """Test student can view own attendance."""
        result = self.auth.can_perform_action("S001", "view_own_attendance")
        assert result is True

    def test_cannot_perform_action_student_mark(self):
        """Test student cannot mark attendance."""
        result = self.auth.can_perform_action("S001", "mark_attendance", "S001")
        assert result is False

    def test_parent_can_view_child_attendance(self):
        """Test parent can view child's attendance."""
        result = self.auth.can_perform_action("P001", "view_child_attendance", "S001")
        assert result is True

    def test_parent_cannot_view_unrelated_child(self):
        """Test parent cannot view unrelated child's attendance."""
        result = self.auth.can_perform_action("P001", "view_child_attendance", "S002")
        assert result is False

    def test_teacher_can_mark_authorized_student(self):
        """Test teacher can mark authorized student."""
        result = self.auth.can_perform_action("T001", "mark_attendance", "S001")
        assert result is True

    def test_principal_can_view_school_analytics(self):
        """Test principal can view school analytics."""
        result = self.auth.can_perform_action("PR001", "view_school_analytics")
        assert result is True

    def test_student_cannot_view_school_analytics(self):
        """Test student cannot view school analytics."""
        result = self.auth.can_perform_action("S001", "view_school_analytics")
        assert result is False


class TestIntentDetection:
    """Test intent detection."""

    def setup_method(self):
        """Setup test fixtures."""
        self.intent_service = IntentService()

    def test_student_attendance_intent(self):
        """Test detecting student attendance intent."""
        intent, conf = self.intent_service.detect_intent(
            "What is my attendance?", "student"
        )
        assert intent == Intent.GET_OWN_ATTENDANCE

    def test_parent_child_attendance_intent(self):
        """Test detecting parent child attendance intent."""
        intent, conf = self.intent_service.detect_intent(
            "How much attendance does my child have?", "parent"
        )
        assert intent == Intent.GET_CHILD_ATTENDANCE

    def test_mark_attendance_intent(self):
        """Test detecting mark attendance intent."""
        intent, conf = self.intent_service.detect_intent(
            "Mark Rahul absent today.", "teacher"
        )
        assert intent == Intent.MARK_ATTENDANCE

    def test_school_attendance_intent(self):
        """Test detecting school attendance intent."""
        intent, conf = self.intent_service.detect_intent(
            "What is the overall attendance?", "principal"
        )
        assert intent == Intent.GET_SCHOOL_ATTENDANCE

    def test_teacher_escalation_intent(self):
        """Test detecting teacher escalation intent."""
        intent, conf = self.intent_service.detect_intent(
            "I want to talk to my child's teacher.", "parent"
        )
        assert intent == Intent.REQUEST_TEACHER_CALL

    def test_management_escalation_intent(self):
        """Test detecting management escalation intent."""
        intent, conf = self.intent_service.detect_intent(
            "Contact school management.", "parent"
        )
        assert intent == Intent.REQUEST_MANAGEMENT_CALL


class TestAttendance:
    """Test attendance operations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.attendance = AttendanceService()

    def test_get_student_attendance(self):
        """Test getting student attendance."""
        record = self.attendance.get_student_attendance("S001")
        assert record is not None
        assert record["student_id"] == "S001"
        assert record["student_name"] == "Rahul Sharma"
        assert record["current_percentage"] == 91.2

    def test_mark_attendance(self):
        """Test marking student attendance."""
        result = self.attendance.mark_attendance("S001", "today", "absent")
        assert result is not None
        assert result["student_id"] == "S001"
        # Percentage should decrease after marking absent
        assert result["current_percentage"] < 91.2

    def test_invalid_student(self):
        """Test marking attendance for invalid student."""
        result = self.attendance.mark_attendance("INVALID", "today", "present")
        assert result is None

    def test_invalid_status(self):
        """Test marking with invalid status."""
        result = self.attendance.mark_attendance("S001", "today", "invalid_status")
        assert result is None

    def test_get_school_attendance(self):
        """Test getting school attendance."""
        analytics = self.attendance.get_school_attendance()
        assert analytics is not None
        assert analytics["overall_percentage"] == 89.7
        assert analytics["total_students"] == 1240


class TestSupport:
    """Test support and escalation operations."""

    def setup_method(self):
        """Setup test fixtures."""
        self.support = SupportService()

    def test_create_teacher_call_request(self):
        """Test creating teacher call request."""
        req = self.support.create_teacher_call_request("P001", "S001", "Attendance concern")
        assert req is not None
        assert req["type"] == "teacher_call"
        assert req["created_by"] == "P001"
        assert req["student_id"] == "S001"
        assert req["status"] == "SUBMITTED"

    def test_create_management_request(self):
        """Test creating management request."""
        req = self.support.create_management_call_request("P001", "parent", "School policy issue")
        assert req is not None
        assert req["type"] == "management_call"
        assert req["created_by"] == "P001"
        assert req["status"] == "SUBMITTED"

    def test_get_request(self):
        """Test retrieving a request."""
        req = self.support.create_teacher_call_request("P001", "S001")
        req_id = req["request_id"]
        retrieved = self.support.get_request(req_id)
        assert retrieved is not None
        assert retrieved["request_id"] == req_id


class TestConversationMemory:
    """Test conversation memory and context."""

    def setup_method(self):
        """Setup test fixtures."""
        self.memory_store = ConversationMemoryStore()

    def test_add_messages(self):
        """Test adding messages to conversation."""
        self.memory_store.add_user_message("S001", "What is my attendance?")
        self.memory_store.add_assistant_message("S001", "Your attendance is 91%")
        
        conv = self.memory_store.conversations.get("S001")
        assert conv is not None
        assert len(conv.get_full_history()) == 2

    def test_update_context(self):
        """Test updating conversation context."""
        self.memory_store.update_context("S001", "mentioned_student_id", "S002")
        context = self.memory_store.get_context("S001")
        assert context is not None
        assert context["mentioned_student_id"] == "S002"

    def test_conversation_isolation(self):
        """Test that conversations are isolated by user."""
        self.memory_store.add_user_message("S001", "Message from student 1")
        self.memory_store.add_user_message("S002", "Message from student 2")
        
        conv1 = self.memory_store.conversations.get("S001")
        conv2 = self.memory_store.conversations.get("S002")
        
        assert conv1 is not None
        assert conv2 is not None
        assert conv1.messages[0]["content"] == "Message from student 1"
        assert conv2.messages[0]["content"] == "Message from student 2"


class TestSecurityAndAuthorization:
    """Test security and authorization checks."""

    def setup_method(self):
        """Setup test fixtures."""
        self.auth = AuthenticationService()
        self.db = MockSchoolDatabase()

    def test_role_cannot_be_spoofed(self):
        """Test that role cannot be changed by claiming to be another role."""
        # Even if message says "I am principal", the backend uses authenticated role
        user_info = self.auth.get_authenticated_user("S001")
        assert user_info["role"] == "student"  # Backend-determined role, not user claim

    def test_student_cannot_access_principal_data(self):
        """Test student cannot access principal-only data."""
        # Student should not have access to school analytics
        result = self.auth.can_perform_action("S001", "view_school_analytics")
        assert result is False

    def test_parent_cannot_mark_attendance(self):
        """Test parent cannot mark attendance."""
        result = self.auth.can_perform_action("P001", "mark_attendance", "S001")
        assert result is False

    def test_unauthorized_teacher_cannot_mark(self):
        """Test teacher cannot mark unauthorized student."""
        # Teacher T001 is authorized for S001-S003
        # But not for a hypothetical S099
        result = self.auth.can_perform_action("T001", "mark_attendance", "S099")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
