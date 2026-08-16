"""
Intent detection and entity extraction.
Converts natural language to structured intents and entities.
"""
import re
from enum import Enum
from mock_data import MockSchoolDatabase


class Intent(Enum):
    """Supported intents in the system."""
    GET_OWN_ATTENDANCE = "get_own_attendance"
    GET_CHILD_ATTENDANCE = "get_child_attendance"
    GET_STUDENT_ATTENDANCE = "get_student_attendance"
    MARK_ATTENDANCE = "mark_attendance"
    GET_RECENT_ATTENDANCE = "get_recent_attendance"
    GET_SCHOOL_ATTENDANCE = "get_school_attendance"
    GET_ATTENDANCE_ANALYTICS = "get_attendance_analytics"
    GET_CLASS_ATTENDANCE = "get_class_attendance"
    REQUEST_TEACHER_CALL = "request_teacher_call"
    REQUEST_MANAGEMENT_CALL = "request_management_call"
    GENERAL_HELP = "general_help"
    CLARIFICATION = "clarification"
    UNKNOWN = "unknown"


class IntentService:
    """Detects user intent and extracts relevant entities."""

    # Intent confidence thresholds
    MIN_CONFIDENCE = 0.4

    def __init__(self):
        """Initialize intent service."""
        self.db = MockSchoolDatabase()

    def detect_intent(self, message, role, session_context=None):
        """
        Detect the intent behind a user's message.
        Returns: (intent, confidence)
        """
        if not message or not message.strip():
            return Intent.GENERAL_HELP, 0.0

        lower = message.lower()

        # Escalation intents (check first - highest priority)
        if self._is_teacher_escalation(lower):
            return Intent.REQUEST_TEACHER_CALL, 0.95
        
        if self._is_management_escalation(lower):
            return Intent.REQUEST_MANAGEMENT_CALL, 0.95

        # Attendance marking (check for action intent)
        if self._is_mark_attendance(lower):
            return Intent.MARK_ATTENDANCE, 0.90

        # School-wide analytics
        if self._is_school_attendance(lower):
            return Intent.GET_SCHOOL_ATTENDANCE, 0.90

        # Follow-up attendance questions
        if self._is_recent_attendance(lower):
            return Intent.GET_RECENT_ATTENDANCE, 0.85

        # Class attendance questions
        if self._is_class_attendance_query(lower):
            return Intent.GET_CLASS_ATTENDANCE, 0.80

        # Role-specific attendance queries
        if "attendance" in lower or "marks" in lower:
            if role == "principal":
                return Intent.GET_SCHOOL_ATTENDANCE, 0.85
            if role == "parent":
                if self._is_child_attendance_query(lower):
                    return Intent.GET_CHILD_ATTENDANCE, 0.85
            if role == "student":
                return Intent.GET_OWN_ATTENDANCE, 0.90
            if role == "teacher":
                return Intent.GET_STUDENT_ATTENDANCE, 0.85
            return Intent.GET_STUDENT_ATTENDANCE, 0.70

        # Greetings and help
        if self._is_greeting(lower):
            return Intent.GENERAL_HELP, 0.80

        return Intent.UNKNOWN, 0.50

    def extract_entities(self, message, role, session_context=None):
        """
        Extract entities from a message.
        Returns: dict with entity types and values
        """
        entities = {
            "student_id": None,
            "student_name": None,
            "status": None,
            "date": None,
            "time_period": None,
            "child_name": None,
        }

        if not message or not message.strip():
            return entities

        lower = message.lower()

        # Extract attendance status
        status_match = re.search(r"\b(absent|present|leave)\b", lower)
        if status_match:
            entities["status"] = status_match.group(1).lower()

        # Extract date references
        if re.search(r"\btoday\b", lower):
            entities["date"] = "today"
        elif re.search(r"\byesterday\b", lower):
            entities["date"] = "yesterday"
        elif re.search(r"\b(last month|this month)\b", lower):
            entities["time_period"] = "last month" if "last" in lower else "this month"

        # Extract student names
        student_name = self._extract_student_name(lower)
        if student_name:
            entities["student_name"] = student_name
            entities["student_id"] = self._resolve_student_id(student_name)

        # For child queries, remember if context indicates child relationship
        if role == "parent":
            if "child" in lower or "son" in lower or "daughter" in lower:
                if student_name:
                    entities["child_name"] = student_name

        # Use session context to remember current student
        if session_context:
            if not entities["student_id"] and session_context.get("current_student_id"):
                entities["student_id"] = session_context["current_student_id"]
                entities["student_name"] = session_context.get("current_student_name")

        return entities

    def _is_mark_attendance(self, lower):
        """Check if message is about marking attendance."""
        mark_pattern = r"\b(mark|record|set|update)\b.*\b(absent|present|leave)\b|\b(absent|present|leave)\b.*\b(mark|record)\b"
        return bool(re.search(mark_pattern, lower))

    def _is_teacher_escalation(self, lower):
        """Check if message is asking for teacher escalation."""
        patterns = [
            r"\b(talk.*to|contact|call|speak.*to|request)\b.*\b(teacher|sir|madam)\b",
            r"\b(teacher|sir|madam)\b.*\b(talk|contact|call|speak|request)\b",
            r"\b(not satisfied|dissatisfied|unhappy)\b.*\b(teacher|talk|contact)\b",
            r"\b(want.*to|would.*like.*to)\b.*\b(talk|speak|contact)\b.*\b(teacher|sir)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_management_escalation(self, lower):
        """Check if message is asking for management escalation."""
        patterns = [
            r"\b(school|management|principal|administration)\b",
            r"\b(talk.*to|contact|call|speak.*to)\b.*\b(management|principal)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns) and ("management" in lower or "principal" in lower)

    def _is_school_attendance(self, lower):
        """Check if asking for school-wide attendance."""
        patterns = [
            r"\b(overall|school|entire school)\b.*\b(attendance|average)\b",
            r"\b(attendance|average)\b.*\b(overall|school|entire school)\b",
            r"\b(which class|average class)\b.*\b(attendance|attendance rate)\b",
            r"\b(how many students)\b.*\b(below|under)\b.*\b(attendance|percent)\b",
            r"\b(today['s]?|today's)\b.*\b(attendance|summary|report)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_recent_attendance(self, lower):
        """Check if asking for recent/historical attendance."""
        patterns = [
            r"\b(what about|recently|last month|this month|previous|history)\b",
            r"\b(recent|historical)\b.*\b(attendance|record)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_class_attendance_query(self, lower):
        """Check if asking about class-specific attendance."""
        patterns = [
            r"\b(which class|grade)\b.*\b(attendance|lowest|highest)\b",
            r"\b(class|grade)\b.*\b(attendance|lowest|highest)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_child_attendance_query(self, lower):
        """Check if parent is asking about their child."""
        patterns = [
            r"\b(my child|our child|the child|son|daughter)\b",
            r"\b(child['s]?|child's)\b.*\b(attendance|record)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_greeting(self, lower):
        """Check if message is a greeting."""
        greetings = [
            "hello", "hi", "hey", "namaste", "vanakkam", "namaskaram",
            "good morning", "good afternoon", "good evening",
        ]
        return any(greeting in lower for greeting in greetings)

    def _extract_student_name(self, lower):
        """Extract student name from message."""
        all_students = self.db.get_all_students()

        # First name variations
        for student in all_students:
            first_name = student["name"].split()[0].lower()
            if first_name in lower:
                return student["name"]

        # Full name check
        for student in all_students:
            if student["name"].lower() in lower:
                return student["name"]

        return None

    def _resolve_student_id(self, student_name):
        """Resolve a student name to ID."""
        all_students = self.db.get_all_students()
        for student in all_students:
            if student["name"].lower() == student_name.lower():
                return student["student_id"]
        return None

    def resolve_student_by_name(self, student_name):
        """Resolve a student name to the full student object."""
        all_students = self.db.get_all_students()
        # Exact match first
        for student in all_students:
            if student["name"].lower() == student_name.lower():
                return student
        # Partial match
        for student in all_students:
            if student["name"].lower().startswith(student_name.lower()):
                return student
        return None

