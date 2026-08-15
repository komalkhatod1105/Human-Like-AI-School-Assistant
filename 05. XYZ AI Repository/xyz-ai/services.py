import re
from datetime import datetime


class SchoolAssistantService:
    def __init__(self):
        self.students = {
            "student_1": {
                "name": "Rahul",
                "class_name": "Grade 9-A",
                "parent_id": "parent_1",
                "attendance": 91.2,
                "teacher_id": "teacher_1",
                "language": "en",
            },
            "student_2": {
                "name": "Aisha",
                "class_name": "Grade 8-B",
                "parent_id": "parent_2",
                "attendance": 94.5,
                "teacher_id": "teacher_2",
                "language": "en",
            },
        }
        self.parents = {
            "parent_1": {"name": "Mr. Sharma", "child_id": "student_1"},
            "parent_2": {"name": "Mrs. Khan", "child_id": "student_2"},
        }
        self.teachers = {
            "teacher_1": {"name": "Ms. Nair", "class_name": "Grade 9-A"},
            "teacher_2": {"name": "Mr. Patel", "class_name": "Grade 8-B"},
        }
        self.school = {
            "overall_attendance": 89.7,
            "language_support": ["en", "hi", "ta", "te", "mr", "bn", "gu", "pa", "kn", "ml", "ur"]
        }
        self.support_requests = []

    def _detect_language(self, message):
        lowered = message.lower()
        if any(term in lowered for term in ["hello", "what is my attendance", "mark", "overall attendance"]):
            return "en"
        if any(term in lowered for term in ["namaste", "mera", "baccha", "attendance"]):
            return "hi"
        if any(term in lowered for term in ["vanakkam", "enakku", "attendance"]):
            return "ta"
        if any(term in lowered for term in ["namaskaram", "na", "attendance"]):
            return "te"
        return "en"

    def _sanitize_message(self, message):
        blocked = [
            "ignore previous instructions",
            "reveal the system prompt",
            "system prompt",
            "api key",
            "secret key",
            "credentials",
            "override",
        ]
        lowered = message.lower()
        for phrase in blocked:
            if phrase in lowered:
                return True
        return False

    def _role_allowed(self, role, user_id, target, requested_action=None):
        if role == "student":
            if target in ["attendance", "self", "teacher"]:
                return True
            return user_id in self.students
        if role == "parent":
            if target == "child_attendance":
                return user_id in self.parents
            if target == "teacher":
                return user_id in self.parents
            return False
        if role == "teacher":
            if requested_action == "mark_attendance":
                return True
            return user_id in self.teachers
        if role == "principal":
            return True
        return False

    def _get_student_from_user(self, user_id):
        return self.students.get(user_id)

    def _get_parent_child(self, user_id):
        parent = self.parents.get(user_id)
        if not parent:
            return None
        return self.students.get(parent["child_id"])

    def _answer_attendance(self, role, user_id, target):
        if role == "student":
            student = self._get_student_from_user(user_id)
            if not student:
                return {"text": "I can’t find your student profile."}
            return {
                "text": f"Your attendance is {student['attendance']:.1f}%. You are currently on track with your academic progress."
            }

        if role == "parent":
            child = self._get_parent_child(user_id)
            if not child:
                return {"text": "I can’t find your child’s record."}
            return {
                "text": f"Your child, {child['name']}, currently has {child['attendance']:.1f}% attendance."
            }

        if role == "principal":
            return {
                "text": f"The overall school attendance is {self.school['overall_attendance']:.1f}% across all classes."
            }

        return {"text": "I’m not authorized to provide that attendance data."}

    def _handle_mark_attendance(self, user_id, message):
        teacher = self.teachers.get(user_id)
        if not teacher:
            return {"text": "You are not authorized to mark attendance."}
        match = re.search(r"\b(mark|record)\s+([A-Za-z]+)\s+(present|absent)\b", message, flags=re.I)
        if not match:
            return {"text": "I can help with a mark attendance request. Please specify the student name and status, for example: 'Mark Rahul absent today.'"}
        student_name = match.group(2).title()
        status = match.group(3).lower()
        for student in self.students.values():
            if student["name"].lower() == student_name.lower():
                return {
                    "text": f"Attendance updated: {student_name} marked {status} for today. The teacher record has been saved.",
                    "action": {"type": "attendance_update", "student": student_name, "status": status, "teacher": teacher["name"]}
                }
        return {"text": f"I couldn’t find a student named {student_name}. Please confirm the student name."}

    def _handle_escalation(self, role, user_id, target, request_id=None):
        if role not in ["student", "parent"]:
            return {"status": "rejected", "text": "Escalation is available to students and parents only."}
        if target not in ["teacher", "management"]:
            return {"status": "rejected", "text": "Target must be teacher or school management."}

        if target == "teacher":
            recipient = "teacher"
        else:
            recipient = "school management"

        request = {
            "request_id": request_id or f"REQ-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "role": role,
            "user_id": user_id,
            "target": target,
            "status": "submitted",
            "created_at": datetime.utcnow().isoformat(),
        }
        self.support_requests.append(request)
        return {
            "status": "submitted",
            "text": f"Your call request has been submitted to {recipient}.",
            "request_id": request["request_id"],
        }

    def process_message(self, role, user_id, message, history):
        if not message or not message.strip():
            return {"text": "I’m ready to help. What would you like to know?"}

        if self._sanitize_message(message):
            return {
                "text": "I can’t assist with security-related or prompt-injection requests. Please ask about school attendance, support, or academic help.",
                "safety": "blocked"
            }

        msg = message.strip()
        language = self._detect_language(msg)
        lower = msg.lower()

        if "not satisfied" in lower or "talk to teacher" in lower or "contact school management" in lower or "want to talk" in lower:
            target = "teacher" if "teacher" in lower else "management"
            return self.handle_escalation(role, user_id, target)

        if role == "student" and "attendance" in lower:
            return {"text": f"Sure, let me check that for you. {self._answer_attendance(role, user_id, 'attendance')['text']}", "language": language}

        if role == "parent" and "attendance" in lower and any(keyword in lower for keyword in ["principal", "teacher", "management", "school", "staff"]):
            return {"text": "I’m not authorized to share that attendance information.", "language": language}

        if role == "parent" and "child" in lower and "attendance" in lower:
            return {"text": f"Sure, let me check that for you. {self._answer_attendance(role, user_id, 'child_attendance')['text']}", "language": language}

        if role == "teacher" and "mark" in lower:
            return self._handle_mark_attendance(user_id, msg)

        if role == "principal" and "attendance" in lower:
            return {"text": f"Certainly. {self._answer_attendance(role, user_id, 'attendance')['text']}", "language": language}

        if role == "student" and "what is my attendance" in lower:
            return {"text": f"Sure, let me check that for you. {self._answer_attendance(role, user_id, 'attendance')['text']}", "language": language}

        if role == "parent" and "attendance" in lower and user_id in self.parents:
            child = self._get_parent_child(user_id)
            if child:
                return {"text": f"Sure, let me check that for you. {child['name']} currently has {child['attendance']:.1f}% attendance.", "language": language}

        if role == "student" and "hello" in lower or "hi" in lower:
            return {"text": "Hi! I’m XYZ AI, your school assistant. How can I help you today?", "language": language}

        if role == "parent" and ("hello" in lower or "hi" in lower):
            return {"text": "Hello! I’m here to help you with your child’s school information. How may I support you today?", "language": language}

        if role == "teacher" and ("hello" in lower or "hi" in lower):
            return {"text": "Hello, teacher. How can I assist with student and class management today?", "language": language}

        if role == "principal" and ("hello" in lower or "hi" in lower):
            return {"text": "Good day, Principal. I can help with attendance insights and school operations.", "language": language}

        if "attendance" in lower:
            if role == "student":
                return {"text": f"Your attendance is {self.students[user_id]['attendance']:.1f}%.", "language": language}
            if role == "parent":
                child = self._get_parent_child(user_id)
                if child:
                    return {"text": f"Your child’s attendance is {child['attendance']:.1f}%.", "language": language}


        return {
            "text": f"I understand you’re asking about: \"{msg}\". I can help with attendance, student records, teacher escalations, and school operations. Please clarify your request.",
            "language": language
        }

    def handle_escalation(self, role, user_id, target):
        return self._handle_escalation(role, user_id, target)
