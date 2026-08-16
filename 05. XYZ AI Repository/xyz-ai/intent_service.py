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

        # Attendance marking (check early - high priority action)
        if self._is_mark_attendance(lower):
            return Intent.MARK_ATTENDANCE, 0.90

        # School-wide analytics (check before general escalations)
        if self._is_school_attendance(lower):
            return Intent.GET_SCHOOL_ATTENDANCE, 0.90

        # Attendance queries (check before escalations, but with role-specific handling)
        if "attendance" in lower or "marks" in lower:
            if role == "principal":
                return Intent.GET_SCHOOL_ATTENDANCE, 0.85
            if role == "parent":
                if self._is_child_attendance_query(lower):
                    return Intent.GET_CHILD_ATTENDANCE, 0.85
                # Parent asking about non-child attendance (will be denied or checked)
                return Intent.GET_STUDENT_ATTENDANCE, 0.75
            if role == "student":
                # If student explicitly names another student, treat as GET_STUDENT_ATTENDANCE (will be denied)
                # Otherwise, treat as GET_OWN_ATTENDANCE
                if self._names_another_student(lower):
                    return Intent.GET_STUDENT_ATTENDANCE, 0.85
                return Intent.GET_OWN_ATTENDANCE, 0.90
            if role == "teacher":
                return Intent.GET_STUDENT_ATTENDANCE, 0.85
            return Intent.GET_STUDENT_ATTENDANCE, 0.70

        # Follow-up attendance questions (check after specific queries)
        if self._is_recent_attendance(lower):
            return Intent.GET_RECENT_ATTENDANCE, 0.85

        # Class attendance questions
        if self._is_class_attendance_query(lower):
            return Intent.GET_CLASS_ATTENDANCE, 0.80

        # Escalation intents (check AFTER attendance queries to avoid false positives)
        if self._is_teacher_escalation(lower):
            return Intent.REQUEST_TEACHER_CALL, 0.95
        
        if self._is_management_escalation(lower):
            return Intent.REQUEST_MANAGEMENT_CALL, 0.95

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
        status_patterns = {
            "present": [r"\bpresent\b", r"\bmarked\s+present\b"],
            "absent": [r"\babsent\b", r"\bmarked\s+absent\b", r"\bno show\b"],
            "leave": [r"\bleave\b", r"\bon\s+leave\b", r"\bleave\s+application\b"],
        }
        
        for status, patterns in status_patterns.items():
            for pattern in patterns:
                if re.search(pattern, lower):
                    entities["status"] = status
                    break

        # Extract date references
        date_patterns = {
            "today": [r"\btoday\b", r"\btoday['s]?\b"],
            "yesterday": [r"\byesterday\b"],
            "tomorrow": [r"\btomorrow\b"],
        }
        
        for date_ref, patterns in date_patterns.items():
            for pattern in patterns:
                if re.search(pattern, lower):
                    entities["date"] = date_ref
                    break

        # Extract time periods
        if re.search(r"\blast\s+month\b", lower):
            entities["time_period"] = "last month"
        elif re.search(r"\bthis\s+month\b", lower):
            entities["time_period"] = "this month"
        elif re.search(r"\blast\s+week\b", lower):
            entities["time_period"] = "last week"
        elif re.search(r"\bthis\s+week\b", lower):
            entities["time_period"] = "this week"
        elif re.search(r"\blast\s+\d+\s+days?\b", lower):
            match = re.search(r"last\s+(\d+)\s+days?", lower)
            if match:
                entities["time_period"] = f"last {match.group(1)} days"

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
            r"\b(talk.*to|contact|call|speak.*to|request|connect)\b.*\b(teacher|sir|madam|instructor)\b",
            r"\b(teacher|sir|madam|instructor)\b.*\b(talk|contact|call|speak|request|connect)\b",
            r"\b(not satisfied|dissatisfied|unhappy|concerned)\b.*\b(teacher|talk|contact|speak)\b",
            r"\b(want.*to|would.*like.*to|need.*to|can.*i)\b.*\b(talk|speak|contact)\b.*\b(teacher|sir|madam)\b",
            r"\b(escalate|escalation)\b.*\b(teacher|instructor)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_management_escalation(self, lower):
        """Check if message is asking for management escalation."""
        patterns = [
            r"\b(talk.*to|contact|call|speak.*to|request|connect)\b.*\b(management|principal|administration|school)\b",
            r"\b(management|principal|administration)\b.*\b(talk|contact|call|speak|request|connect)\b",
            r"\b(escalate|escalation)\b.*\b(management|principal)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_school_attendance(self, lower):
        """Check if asking for school-wide attendance."""
        patterns = [
            r"\b(overall|school|entire\s+school|entire|all)\b.*\b(attendance|average|statistics|stats)\b",
            r"\b(attendance|average|statistics|stats)\b.*\b(overall|school|entire\s+school|entire|all)\b",
            r"\b(which class|average class|lowest\s+attendance|highest\s+attendance)\b.*\b(attendance|percentage)\b",
            r"\b(how many students)\b.*\b(below|under|below than|less than)\b.*\b(attendance|percentage|percent)\b",
            r"\b(today['s]?|today's)\b.*\b(attendance|summary|report)\b",
            r"\b(school\s+attendance|overall\s+attendance|general\s+attendance)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_recent_attendance(self, lower):
        """Check if asking for recent/historical attendance."""
        patterns = [
            r"\b(what about|recently|last month|this month|previous|history|previous day|yesterday)\b",
            r"\b(recent|historical)\b.*\b(attendance|record|performance)\b",
            r"\b(show|give|provide)\b.*\b(recent|past)\b.*\b(attendance|record)\b",
            r"\b(last\s+\d+\s+days?|past\s+\d+\s+days?|previous\s+\d+\s+days?)\b.*\b(attendance|record)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_class_attendance_query(self, lower):
        """Check if asking about class-specific attendance."""
        patterns = [
            r"\b(which class|grade|class)\b.*\b(attendance|lowest|highest|best|worst)\b",
            r"\b(attendance|lowest|highest|best|worst)\b.*\b(which class|grade|class)\b",
            r"\b(class.*wise|grade.*wise)\b.*\b(attendance|performance)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_child_attendance_query(self, lower):
        """Check if parent is asking about their child."""
        patterns = [
            r"\b(my child|our child|the child|my son|my daughter|your child)\b",
            r"\b(child['s]?|child's)\b.*\b(attendance|record|performance|marks)\b",
            r"\b(how.*child|how.*son|how.*daughter)\b.*\b(attendance|doing|perform)\b",
            r"\b(what.*child|what.*son|what.*daughter)\b.*\b(attendance|marks|performance)\b",
        ]
        return any(re.search(pattern, lower) for pattern in patterns)

    def _is_greeting(self, lower):
        """Check if message is a greeting."""
        greetings = [
            "hello", "hi", "hey", "namaste", "vanakkam", "namaskaram",
            "good morning", "good afternoon", "good evening",
        ]
        return any(greeting in lower for greeting in greetings)

    def _names_another_student(self, lower):
        """Check if message mentions another student by name."""
        # Extract all student names in the message
        student_names = []
        for student in self.db.get_all_students():
            first_name = student["name"].split()[0].lower()
            if first_name in lower:
                student_names.append(student["name"])
        
        # If at least one student name is mentioned, consider it naming another student
        return len(student_names) > 0

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

