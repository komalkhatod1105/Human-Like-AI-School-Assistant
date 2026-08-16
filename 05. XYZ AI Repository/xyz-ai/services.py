"""
School Assistant Service - Main orchestrator.
Coordinates all services to process user messages and generate responses.
"""
import re
from datetime import datetime, timezone

from auth_service import AuthenticationService
from conversation_service import ConversationService
from intent_service import IntentService, Intent
from language_service import LanguageService
from attendance_service import AttendanceService
from analytics_service import AnalyticsService
from support_service import SupportService
from mock_data import MockSchoolDatabase


class SchoolAssistantService:
    """Main service orchestrator for school assistant."""

    def __init__(self):
        """Initialize all services."""
        self.db = MockSchoolDatabase()
        self.auth = AuthenticationService()
        self.conversation = ConversationService()
        self.intent = IntentService()
        self.language = LanguageService()
        self.attendance = AttendanceService()
        self.analytics = AnalyticsService()
        self.support = SupportService()

        # Security filter patterns
        self.blocked_patterns = [
            r"\b(ignore previous instructions|reveal the system prompt|system prompt)\b",
            r"\b(api key|secret key|credentials|password)\b",
            r"\b(override|bypass|admin|root)\b",
            r"\b(make me principal|make me teacher|make me admin)\b",
            r"\b(show all students|access all data|database query)\b",
        ]

    def process_message(self, user_id, message, history=None, language=None):
        """
        Process a user message and generate a response.
        Main entry point for chat handling.

        Args:
            user_id: The ID of the user
            message: The user's message
            history: Conversation history
            language: Requested language (optional)

        Returns:
            Response dict with text, language, and metadata
        """
        if not message or not message.strip():
            return {
                "text": "I'm ready to help. What would you like to know?",
                "language": language or "en",
            }

        # Authenticate user (backend determines role)
        user_info = self.auth.get_authenticated_user(user_id)
        if not user_info:
            return {
                "text": "I couldn't authenticate your session. Please try again.",
                "error": "authentication_failed",
            }

        user_id_normalized = user_info["user_id"]
        role = user_info["role"]

        # Security: Check for prompt injection and blocked phrases
        if self._is_blocked_message(message):
            response_text = (
                "I can't assist with that request. I'm here to help with attendance, "
                "student records, and school support."
            )
            return {
                "text": response_text,
                "safety": "blocked",
                "language": language or "en",
            }

        # Detect language if not provided
        if not language:
            language = self.language.detect_language(message)

        # Get conversation context
        conv_context = self.conversation.get_context(user_id_normalized)

        # Detect intent
        intent, confidence = self.intent.detect_intent(message, role)

        # Extract entities
        entities = self.intent.extract_entities(message, role, conv_context)

        # Process intent and generate response
        response = self._handle_intent(
            role, user_id_normalized, intent, message, entities, conv_context, language
        )

        # Record interaction
        self.conversation.record_interaction(
            user_id_normalized, role, message, response, intent=intent
        )

        # Add metadata
        response["language"] = language
        response["intent"] = intent.value if isinstance(intent, Intent) else str(intent)

        return response

    def _is_blocked_message(self, message):
        """Check if a message contains blocked patterns (security check)."""
        lower = message.lower()
        for pattern in self.blocked_patterns:
            if re.search(pattern, lower, re.IGNORECASE):
                return True
        return False

    def _handle_intent(self, role, user_id, intent, message, entities, context, language):
        """
        Handle different intent types and generate responses.
        Central handler for all intent types.
        """
        # Get appropriate response template
        if intent == Intent.GET_OWN_ATTENDANCE:
            return self._handle_get_own_attendance(role, user_id, message, language)

        elif intent == Intent.GET_CHILD_ATTENDANCE:
            return self._handle_get_child_attendance(
                role, user_id, message, entities, context, language
            )

        elif intent == Intent.GET_STUDENT_ATTENDANCE:
            return self._handle_get_student_attendance(
                role, user_id, message, entities, context, language
            )

        elif intent == Intent.MARK_ATTENDANCE:
            return self._handle_mark_attendance(role, user_id, message, entities, language)

        elif intent == Intent.GET_SCHOOL_ATTENDANCE:
            return self._handle_get_school_attendance(role, user_id, message, language)

        elif intent == Intent.GET_RECENT_ATTENDANCE:
            return self._handle_get_recent_attendance(role, user_id, context, language)

        elif intent == Intent.REQUEST_TEACHER_CALL:
            return self._handle_escalation(role, user_id, "teacher", message, language)

        elif intent == Intent.REQUEST_MANAGEMENT_CALL:
            return self._handle_escalation(role, user_id, "management", message, language)

        elif intent == Intent.GENERAL_HELP:
            return self._handle_general_help(role, language)

        else:
            return {
                "text": f"I understand you're asking about: '{message}'. "
                "I can help with attendance, records, and escalations. Please clarify your request.",
                "language": language,
            }

    def _handle_get_own_attendance(self, role, user_id, message, language):
        """Handle student requesting their own attendance."""
        if role != "student":
            return {
                "text": self.language.format_response(
                    language, "permission_denied"
                ),
                "status": "denied",
            }

        student = self.db.get_student(user_id)
        if not student:
            return {
                "text": self.language.format_response(
                    language, "student_not_found"
                ),
            }

        # Remember context
        self.conversation.remember_student(user_id, student["student_id"], student["name"])
        self.conversation.remember_topic(user_id, "attendance")

        response_text = self.language.format_response(
            language,
            "attendance_student",
            student_name=student["name"],
            attendance=student["attendance"],
        )

        return {"text": response_text, "status": "success"}

    def _handle_get_child_attendance(self, role, user_id, message, entities, context, language):
        """Handle parent requesting child's attendance."""
        if role != "parent":
            return {
                "text": self.language.format_response(
                    language, "permission_denied"
                ),
                "status": "denied",
            }

        # Get parent's children
        children = self.db.get_parent_children(user_id)
        if not children:
            return {
                "text": self.language.format_response(
                    language, "student_not_found"
                ),
            }

        # Determine which child to report on
        target_student = None

        # If entity has student name, find matching child
        if entities.get("student_name"):
            student_name = entities.get("student_name")
            if student_name:
                student_name_lower = student_name.lower()
                # Try exact match
                for child in children:
                    if child["name"].lower() == student_name_lower:
                        target_student = child
                        break
                # Try startswith match
                if not target_student:
                    for child in children:
                        if child["name"].lower().startswith(student_name_lower):
                            target_student = child
                            break

        # If still no match and only one child, use that child
        if not target_student:
            if len(children) == 1:
                target_student = children[0]
            else:
                # Multiple children, need clarification
                return {
                    "text": f"Which child would you like to check attendance for?",
                    "status": "clarification_required",
                }

        # Remember context
        self.conversation.remember_student(user_id, target_student["student_id"], target_student["name"])
        self.conversation.remember_topic(user_id, "attendance")

        response_text = self.language.format_response(
            language,
            "attendance_student",
            student_name=target_student["name"],
            attendance=target_student["attendance"],
        )

        return {"text": response_text, "status": "success"}

    def _handle_get_student_attendance(self, role, user_id, message, entities, context, language):
        """Handle teacher requesting student's attendance."""
        if role not in ["teacher", "principal", "parent"]:
            return {
                "text": self.language.format_response(
                    language, "permission_denied"
                ),
                "status": "denied",
            }

        # Extract student from entities
        if not entities.get("student_name"):
            return {
                "text": self.language.format_response(
                    language, "clarify_student"
                ),
                "status": "clarification_required",
            }

        # Find student
        all_students = self.db.get_all_students()
        target_student = None
        for student in all_students:
            if student["name"].lower() == entities["student_name"].lower():
                target_student = student
                break

        if not target_student:
            return {
                "text": self.language.format_response(
                    language, "student_not_found"
                ),
            }

        # Check authorization
        if role == "teacher":
            teacher = self.db.get_teacher(user_id)
            if not teacher or target_student["student_id"] not in teacher.get(
                "authorized_student_ids", []
            ):
                return {
                    "text": self.language.format_response(
                        language, "permission_denied"
                    ),
                    "status": "denied",
                }
        elif role == "parent":
            # Check if this student is the parent's child
            parent = self.db.get_parent(user_id)
            if not parent or target_student["student_id"] not in parent.get("child_ids", []):
                return {
                    "text": self.language.format_response(
                        language, "permission_denied"
                    ),
                    "status": "denied",
                }

        # Remember context
        self.conversation.remember_student(user_id, target_student["student_id"], target_student["name"])
        self.conversation.remember_topic(user_id, "attendance")

        response_text = self.language.format_response(
            language,
            "attendance_student",
            student_name=target_student["name"],
            attendance=target_student["attendance"],
        )

        return {"text": response_text, "status": "success"}

    def _handle_mark_attendance(self, role, user_id, message, entities, language):
        """Handle teacher marking attendance."""
        if role != "teacher":
            return {
                "text": self.language.format_response(
                    language, "unauthorized"
                ),
                "status": "denied",
            }

        # Need student name
        if not entities.get("student_name"):
            return {
                "text": self.language.format_response(
                    language, "clarify_student"
                ),
                "status": "clarification_required",
            }

        # Find student
        student = self.intent.resolve_student_by_name(entities["student_name"])
        if not student:
            return {
                "text": self.language.format_response(
                    language, "student_not_found"
                ),
            }

        # Check authorization
        teacher = self.db.get_teacher(user_id)
        if not teacher or student["student_id"] not in teacher.get("authorized_student_ids", []):
            return {
                "text": self.language.format_response(
                    language, "permission_denied"
                ),
                "status": "denied",
            }

        # Need status
        if not entities.get("status"):
            return {
                "text": self.language.format_response(
                    language,
                    "confirm_action",
                    student_name=student["name"],
                ),
                "status": "confirmation_required",
            }

        # Mark attendance
        status = entities["status"]
        date = entities.get("date", "today")

        result = self.attendance.mark_attendance(
            student["student_id"], date, status
        )

        if not result:
            return {
                "text": self.language.format_response(
                    language, "permission_denied"
                ),
                "status": "error",
            }

        # Generate response
        key = "marked_present" if status == "present" else "marked_absent"
        response_text = self.language.format_response(
            language, key, student_name=student["name"]
        )

        return {
            "text": response_text,
            "status": "success",
            "action": {
                "type": "attendance_update",
                "student_id": student["student_id"],
                "status": status,
            },
        }

    def _handle_get_school_attendance(self, role, user_id, message, language):
        """Handle principal requesting school-wide attendance."""
        if role != "principal":
            return {
                "text": self.language.format_response(
                    language, "permission_denied"
                ),
                "status": "denied",
            }

        # Get analytics
        stats = self.analytics.get_school_attendance_stats()
        if not stats.get("success"):
            return {
                "text": "Unable to retrieve school attendance data",
                "error": "analytics_error",
            }

        response_text = self.language.format_response(
            language,
            "attendance_school",
            attendance=stats["overall_attendance"],
            total_students=stats["total_students"],
        )

        return {
            "text": response_text,
            "status": "success",
            "analytics": stats,
        }

    def _handle_get_recent_attendance(self, role, user_id, context, language):
        """Handle follow-up questions about recent attendance."""
        # Get remembered student from context
        remembered = self.conversation.get_remembered_student(user_id)
        student_id = remembered.get("student_id")

        if not student_id:
            return {
                "text": "I need to know which student you're asking about. Could you tell me the student's name?",
                "status": "clarification_required",
            }

        student = self.db.get_student(student_id)
        if not student:
            return {
                "text": self.language.format_response(
                    language, "student_not_found"
                ),
            }

        response_text = self.language.format_response(
            language,
            "attendance_recent",
            student_name=student["name"],
            attendance=student["attendance"],
        )

        return {"text": response_text, "status": "success"}

    def _handle_escalation(self, role, user_id, target, message, language):
        """Handle escalation requests."""
        if role not in ["student", "parent"]:
            return {
                "text": self.language.format_response(
                    language, "permission_denied"
                ),
                "status": "denied",
            }

        # Get child if parent
        student_id = None
        if role == "parent":
            children = self.db.get_parent_children(user_id)
            if children:
                student_id = children[0]["student_id"]

        # Submit escalation
        result = self.support.submit_escalation_request(
            user_id, target, student_id=student_id, reason=message
        )

        if not result.get("success"):
            return {
                "text": result.get("error", "Unable to submit escalation request"),
                "error": "escalation_failed",
            }

        response_text = self.language.format_response(
            language,
            "escalation_submitted",
            target=target,
            request_id=result.get("request_id", ""),
        )

        return {
            "text": response_text,
            "status": "success",
            "action": {
                "type": "escalation",
                "target": target,
                "request_id": result.get("request_id"),
            },
        }

    def _handle_general_help(self, role, language):
        """Handle general greetings and help requests."""
        greeting_keys = {
            "student": "greeting_student",
            "parent": "greeting_parent",
            "teacher": "greeting_teacher",
            "principal": "greeting_principal",
        }

        key = greeting_keys.get(role, "greeting_student")
        response_text = self.language.format_response(language, key)

        return {"text": response_text, "status": "success"}

    # API Methods (for backward compatibility with existing routes)
    def mark_attendance_api(self, student_id, date="today", status="present", teacher_id=None):
        """API endpoint for marking attendance."""
        if not teacher_id:
            return {"success": False, "error": "Teacher ID required"}

        result = self.attendance.mark_attendance(teacher_id, student_id, date, status)
        return result

    def get_school_analytics(self):
        """API endpoint for school analytics."""
        return self.analytics.get_school_attendance_stats()

    def submit_support_request(self, requested_by, target_type, student_id=None, reason=None):
        """API endpoint for support requests."""
        return self.support.submit_escalation_request(
            requested_by, target_type, student_id=student_id, reason=reason
        )

    def get_parent_children(self, parent_id):
        """API endpoint for getting parent's children."""
        children = self.db.get_parent_children(parent_id)
        return {
            "success": True,
            "children": children,
        }

    def get_student(self, student_id):
        """API endpoint for getting student info."""
        student = self.db.get_student(student_id)
        if student:
            return {"success": True, "data": student}
        return {"success": False, "error": "Student not found"}

    def get_student_attendance(self, student_id):
        """API endpoint for getting student attendance."""
        return self.attendance.get_student_attendance(student_id)

    def handle_escalation(self, role, user_id, target):
        """Handle escalation for backward compatibility."""
        return self.support.submit_escalation_request(user_id, target)
