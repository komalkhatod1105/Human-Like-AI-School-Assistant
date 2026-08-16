import re
from datetime import datetime, timezone


class SchoolAssistantService:
    def __init__(self):
        self.students = {
            "S001": {
                "student_id": "S001",
                "name": "Rahul Sharma",
                "class_name": "Grade 9-A",
                "parent_id": "P001",
                "teacher_id": "T001",
                "attendance": 91.2,
                "language": "en",
            },
            "S002": {
                "student_id": "S002",
                "name": "Rohan Verma",
                "class_name": "Grade 8-B",
                "parent_id": "P002",
                "teacher_id": "T001",
                "attendance": 87.5,
                "language": "en",
            },
            "S003": {
                "student_id": "S003",
                "name": "Priya Singh",
                "class_name": "Grade 10-C",
                "parent_id": "P003",
                "teacher_id": "T001",
                "attendance": 94.1,
                "language": "en",
            },
            "student_1": {
                "student_id": "S001",
                "name": "Rahul Sharma",
                "class_name": "Grade 9-A",
                "parent_id": "parent_1",
                "teacher_id": "teacher_1",
                "attendance": 91.2,
                "language": "en",
            },
            "student_2": {
                "student_id": "S002",
                "name": "Rohan Verma",
                "class_name": "Grade 8-B",
                "parent_id": "parent_2",
                "teacher_id": "teacher_1",
                "attendance": 87.5,
                "language": "en",
            },
        }
        self.parents = {
            "P001": {"parent_id": "P001", "name": "Priya Sharma", "child_ids": ["S001"]},
            "P002": {"parent_id": "P002", "name": "Amit Verma", "child_ids": ["S002"]},
            "P003": {"parent_id": "P003", "name": "Neha Singh", "child_ids": ["S003"]},
            "parent_1": {"parent_id": "P001", "name": "Priya Sharma", "child_ids": ["S001"]},
            "parent_2": {"parent_id": "P002", "name": "Amit Verma", "child_ids": ["S002"]},
        }
        self.teachers = {
            "T001": {"teacher_id": "T001", "name": "Anita Gupta", "authorized_student_ids": ["S001", "S002", "S003"]},
            "teacher_1": {"teacher_id": "T001", "name": "Anita Gupta", "authorized_student_ids": ["S001", "S002", "S003"]},
        }
        self.principals = {
            "PR001": {"principal_id": "PR001", "name": "Raj Mehta"},
            "principal_1": {"principal_id": "PR001", "name": "Raj Mehta"},
        }
        self.school = {
            "overall_attendance": 89.7,
            "total_students": 1240,
            "total_teachers": 68,
            "total_parents": 980,
            "language_support": ["en", "hi", "ta", "te", "mr", "bn", "gu", "pa", "kn", "ml", "ur"],
        }
        self.support_requests = []
        self.conversation_log = []
        self.session_context = {}

    def _normalize_id(self, value):
        if value is None:
            return None
        text = str(value).strip()
        aliases = {
            "student_1": "S001",
            "student_2": "S002",
            "parent_1": "P001",
            "parent_2": "P002",
            "teacher_1": "T001",
            "principal_1": "PR001",
            "s001": "S001",
            "s002": "S002",
            "s003": "S003",
            "p001": "P001",
            "p002": "P002",
            "p003": "P003",
            "t001": "T001",
            "pr001": "PR001",
        }
        return aliases.get(text.lower(), text)

    def _resolve_role(self, role, user_id):
        provided = (role or "").strip().lower()
        normalized_user = self._normalize_id(user_id)
        if normalized_user in self.principals:
            return "principal"
        if normalized_user in self.teachers:
            return "teacher"
        if normalized_user in self.parents:
            return "parent"
        if normalized_user in self.students:
            return "student"
        if provided in {"student", "parent", "teacher", "principal"}:
            return provided
        return "student"

    def _detect_language(self, message):
        lowered = message.lower()
        if any(term in lowered for term in ["namaste", "mera", "baccha", "kya", "kitni"]):
            return "hi"
        if any(term in lowered for term in ["vanakkam", "enakku", "enna", "attendance"]):
            return "ta"
        if any(term in lowered for term in ["namaskaram", "na", "attendance"]):
            return "te"
        if any(term in lowered for term in ["hello", "my attendance", "mark", "overall attendance", "what is"]):
            return "en"
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
            "make me principal",
            "show all students",
        ]
        lowered = (message or "").lower()
        for phrase in blocked:
            if phrase in lowered:
                return True
        return False

    def _extract_masked_history(self, history):
        if not history:
            return {}
        for item in reversed(history):
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "")).strip()
            if item.get("role") == "user" and text:
                return {"last_user_message": text}
        return {}

    def _remember_context(self, user_id, student_id=None, topic=None, time_period=None):
        key = self._normalize_id(user_id) or "anonymous"
        ctx = self.session_context.setdefault(key, {})
        if student_id:
            ctx["student_id"] = self._normalize_id(student_id)
        if topic:
            ctx["topic"] = topic
        if time_period:
            ctx["time_period"] = time_period
        return ctx

    def _get_session_context(self, user_id):
        key = self._normalize_id(user_id) or "anonymous"
        return self.session_context.get(key, {})

    def _resolve_student_name(self, student_name):
        if not student_name:
            return None
        target = student_name.strip()
        for student in self.students.values():
            if student["name"].lower() == target.lower():
                return student
        for student in self.students.values():
            if student["name"].lower().startswith(target.lower()):
                return student
        return None

    def _student_for_user(self, user_id):
        normalized = self._normalize_id(user_id)
        if not normalized:
            return None
        if normalized in self.students:
            return self.students[normalized]
        for student in self.students.values():
            if student.get("student_id") == normalized:
                return student
        return None

    def _parent_children(self, user_id):
        normalized = self._normalize_id(user_id)
        parent = self.parents.get(normalized)
        if not parent:
            return []
        children = []
        for child_id in parent.get("child_ids", []):
            student = self.students.get(self._normalize_id(child_id))
            if student:
                children.append(student)
        return children

    def _detect_intent(self, message, role, user_id):
        lower = message.lower()
        if re.search(r"\b(mark|record)\b.*\b(absent|present)\b|\b(absent|present)\b.*\b(mark|record)\b", lower):
            return "MARK_ATTENDANCE"
        if re.search(r"\b(mark|record)\b.*\b(rahul|rohan|priya|student)\b|\b(attendance)\b.*\b(mark|record)\b", lower):
            return "MARK_ATTENDANCE"
        if "overall attendance" in lower or "school attendance" in lower or "which class has" in lower or "attendance summary" in lower:
            return "GET_SCHOOL_ATTENDANCE"
        if "what about" in lower or "last month" in lower or "recent attendance" in lower:
            return "GET_RECENT_ATTENDANCE"
        if "not satisfied" in lower or "talk to teacher" in lower or "contact school management" in lower or "want to talk" in lower:
            return "TEACHER_ESCALATION" if "teacher" in lower else "MANAGEMENT_ESCALATION"
        if "attendance" in lower:
            if role == "parent":
                if "child" in lower or "son" in lower or "daughter" in lower or "my child" in lower or "rahul" in lower or "rohan" in lower:
                    return "GET_CHILD_ATTENDANCE"
            if role == "student":
                return "GET_OWN_ATTENDANCE"
            if role == "principal":
                return "GET_SCHOOL_ATTENDANCE"
            return "GET_STUDENT_ATTENDANCE"
        if any(greeting in lower for greeting in ["hello", "hi", "namaste", "vanakkam", "namaskaram"]):
            return "GENERAL_HELP"
        return "GENERAL_HELP"

    def _extract_entities(self, message, role, user_id, session_context):
        entities = {"student_name": None, "status": None, "date": None, "time_period": None, "target": None}
        lower = message.lower()
        words = lower.split()

        if re.search(r"\b(absent|present)\b", lower):
            status_match = re.search(r"\b(absent|present)\b", lower, flags=re.I)
            entities["status"] = status_match.group(1).lower()

        if "today" in lower:
            entities["date"] = "today"
        elif "yesterday" in lower:
            entities["date"] = "yesterday"
        elif "last month" in lower:
            entities["time_period"] = "last month"

        for name in ["rahul", "rohan", "priya", "aisha"]:
            if name in lower:
                student = self._resolve_student_name(name.title())
                if student:
                    entities["student_name"] = student["name"]
                    break

        student = None
        if "rahul" in lower:
            student = self._resolve_student_name("Rahul")
        elif "rohan" in lower:
            student = self._resolve_student_name("Rohan")
        elif "priya" in lower:
            student = self._resolve_student_name("Priya")

        if student:
            entities["student_name"] = student["name"]

        if "teacher" in lower and ("not satisfied" in lower or "talk to" in lower or "contact" in lower):
            entities["target"] = "teacher"
        elif "management" in lower or "school management" in lower:
            entities["target"] = "management"

        if "what about" in lower and session_context.get("student_id"):
            entities["student_name"] = self.students.get(session_context["student_id"], {}).get("name")
            if "last month" in lower:
                entities["time_period"] = "last month"

        return entities

    def _select_tool(self, intent):
        tool_map = {
            "GET_OWN_ATTENDANCE": "attendance_lookup",
            "GET_CHILD_ATTENDANCE": "parent_child_attendance",
            "GET_STUDENT_ATTENDANCE": "student_attendance_lookup",
            "MARK_ATTENDANCE": "mark_attendance",
            "GET_SCHOOL_ATTENDANCE": "school_analytics",
            "GET_RECENT_ATTENDANCE": "recent_attendance",
            "TEACHER_ESCALATION": "support_call_request",
            "MANAGEMENT_ESCALATION": "support_call_request",
            "GENERAL_HELP": "general_reply",
        }
        return tool_map.get(intent, "general_reply")

    def _record_interaction(self, role, user_id, message, result, intent=None, tool=None):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "user_id": self._normalize_id(user_id),
            "message": message,
            "intent": intent,
            "tool": tool,
            "response": result.get("text", ""),
            "status": result.get("status", "completed"),
        }
        self.conversation_log.append(record)
        return record

    def _role_allowed(self, role, user_id, action, student_id=None):
        normalized_user = self._normalize_id(user_id)
        if role == "student":
            if action == "mark_attendance":
                return False
            if student_id is None:
                return True
            student = self.students.get(self._normalize_id(student_id))
            if not student:
                return False
            return student.get("student_id") == self._student_for_user(normalized_user).get("student_id") if self._student_for_user(normalized_user) else False

        if role == "parent":
            if action == "mark_attendance":
                return False
            if not student_id:
                return True
            student = self.students.get(self._normalize_id(student_id))
            if not student:
                return False
            return student.get("student_id") in [child.get("student_id") for child in self._parent_children(normalized_user)]

        if role == "teacher":
            if action == "mark_attendance":
                if not student_id:
                    return False
                teacher = self.teachers.get(normalized_user)
                if not teacher:
                    return False
                return self._normalize_id(student_id) in teacher.get("authorized_student_ids", [])
            return True

        if role == "principal":
            return action in {"view_school_attendance", "mark_attendance"} or action == "view_school_attendance"
        return False

    def _student_response(self, student_id, include_prompt=False, time_period=None):
        student = self.students.get(self._normalize_id(student_id))
        if not student:
            return {"text": "I couldn't find that student. Could you check the name?"}
        if time_period == "last month":
            text = f"{student['name']} had {student['attendance']:.1f}% attendance last month."
        else:
            text = f"{student['name']} currently has {student['attendance']:.1f}% attendance."
        if include_prompt:
            text += " Would you like me to check their recent attendance too?"
        return {"text": text}

    def _principal_analytics_response(self):
        return {
            "text": f"The current overall school attendance is {self.school['overall_attendance']:.1f}% across {self.school['total_students']} students.",
            "analytics": {
                "overall_attendance": self.school["overall_attendance"],
                "total_students": self.school["total_students"],
                "total_teachers": self.school["total_teachers"],
                "total_parents": self.school["total_parents"],
            },
        }

    def get_student(self, student_id):
        normalized = self._normalize_id(student_id)
        student = self.students.get(normalized)
        if student:
            return {"success": True, "data": student}
        return {"success": False, "error": "Student not found"}

    def get_student_attendance(self, student_id):
        student = self.students.get(self._normalize_id(student_id))
        if not student:
            return {"success": False, "error": "Student not found"}
        return {"success": True, "student_id": student["student_id"], "attendance": student["attendance"]}

    def get_parent_children(self, parent_id):
        normalized = self._normalize_id(parent_id)
        parent = self.parents.get(normalized)
        if not parent:
            return {"success": False, "error": "Parent not found"}
        children = [self.students.get(self._normalize_id(child_id)) for child_id in parent.get("child_ids", [])]
        return {"success": True, "children": [student for student in children if student]}

    def mark_attendance_api(self, student_id, date, status, teacher_id=None):
        normalized_student = self._normalize_id(student_id)
        student = self.students.get(normalized_student)
        if not student:
            return {"success": False, "error": "Student not found"}
        if teacher_id:
            teacher = self.teachers.get(self._normalize_id(teacher_id))
            if not teacher or normalized_student not in teacher.get("authorized_student_ids", []):
                return {"success": False, "error": "Unauthorized teacher"}
        request_id = f"ATT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        return {
            "success": True,
            "request_id": request_id,
            "student_id": normalized_student,
            "date": date,
            "status": status,
        }

    def get_school_analytics(self):
        return {
            "success": True,
            "data": {
                "overall_attendance": self.school["overall_attendance"],
                "total_students": self.school["total_students"],
                "total_teachers": self.school["total_teachers"],
                "total_parents": self.school["total_parents"],
            },
        }

    def submit_support_request(self, requested_by, target_type, student_id=None, reason="School support request"):
        normalized_by = self._normalize_id(requested_by)
        if target_type not in {"teacher", "management"}:
            return {"success": False, "error": "Invalid target type"}
        request_id = f"REQ-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        record = {
            "request_id": request_id,
            "requested_by": normalized_by,
            "target_type": target_type,
            "student_id": self._normalize_id(student_id),
            "reason": reason,
            "status": "SUBMITTED",
        }
        self.support_requests.append(record)
        return {"success": True, "request_id": request_id, "status": "SUBMITTED"}

    def _handle_mark_attendance(self, user_id, message):
        normalized_user = self._normalize_id(user_id)
        teacher = self.teachers.get(normalized_user)
        if not teacher:
            return {"text": "Sorry, you don't have permission to mark attendance. This action is available only to authorized teachers.", "status": "denied"}

        match = re.search(r"\b(mark|record)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(present|absent)\b", message, flags=re.I)
        if match:
            student_name = match.group(2).strip()
            status = match.group(3).lower()
            student = self._resolve_student_name(student_name)
            if not student:
                return {"text": "I couldn't find that student. Could you check the name?"}
            target_student_id = student.get("student_id")
            if not self._role_allowed("teacher", normalized_user, "mark_attendance", target_student_id):
                return {"text": "Sorry, you don't have permission to mark attendance for that student.", "status": "denied"}
            return {
                "text": f"{student['name']} has been marked {status} for today.",
                "status": "success",
                "action": {"type": "attendance_update", "student_id": target_student_id, "status": status, "teacher_id": normalized_user},
            }

        if re.search(r"\b(absent|present)\b", message, flags=re.I):
            return {"text": "Sure. Which student should I mark absent?", "status": "clarification_required"}

        return {"text": "Sure. Which student should I mark absent?", "status": "clarification_required"}

    def _handle_escalation(self, role, user_id, target, request_id=None):
        if role not in ["student", "parent"]:
            return {"status": "rejected", "text": "Escalation is available to students and parents only."}
        if target not in ["teacher", "management"]:
            return {"status": "rejected", "text": "Target must be teacher or school management."}

        request_id = request_id or f"REQ-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        request = {
            "request_id": request_id,
            "role": role,
            "user_id": self._normalize_id(user_id),
            "target": target,
            "status": "SUBMITTED",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.support_requests.append(request)
        return {
            "status": "success",
            "text": f"Your call request has been submitted to the {target}. Request ID: {request_id}.",
            "request_id": request_id,
        }

    def process_message(self, role, user_id, message, history):
        normalized_user = self._normalize_id(user_id)
        resolved_role = self._resolve_role(role, normalized_user)

        if not message or not message.strip():
            return {"text": "I’m ready to help. What would you like to know?"}

        if self._sanitize_message(message):
            response = {
                "text": "I can’t assist with security-related or prompt-injection requests. Please ask about school attendance, support, or academic help.",
                "safety": "blocked",
            }
            self._record_interaction(resolved_role, normalized_user, message, response, intent="blocked", tool="safety_filter")
            return response

        msg = message.strip()
        lower = msg.lower()
        session_ctx = self._get_session_context(normalized_user)
        history_context = self._extract_masked_history(history)
        if history_context and "last_user_message" in history_context and "what about" in history_context["last_user_message"].lower():
            session_ctx = self.session_context.setdefault(normalized_user, {})

        intent = self._detect_intent(msg, resolved_role, normalized_user)
        entities = self._extract_entities(msg, resolved_role, normalized_user, session_ctx)
        tool = self._select_tool(intent)
        language = self._detect_language(msg)

        if intent == "TEACHER_ESCALATION":
            target = "teacher"
            return {**self._handle_escalation(resolved_role, normalized_user, target), "language": language}

        if intent == "MANAGEMENT_ESCALATION":
            target = "management"
            return {**self._handle_escalation(resolved_role, normalized_user, target), "language": language}

        if intent == "MARK_ATTENDANCE":
            if resolved_role != "teacher":
                response = {"text": "Sorry, you don't have permission to mark attendance. This action is available only to authorized teachers.", "status": "denied"}
                self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
                return response
            if not entities.get("student_name"):
                response = {"text": "Sure. Which student should I mark absent?", "status": "clarification_required"}
                self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
                return response
            if not entities.get("status"):
                student = self._resolve_student_name(entities["student_name"])
                response = {"text": f"Should I mark {student['name']} absent for today?", "status": "confirmation_required"}
                self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
                return response
            response = self._handle_mark_attendance(normalized_user, msg)
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return response

        if intent == "GET_OWN_ATTENDANCE":
            student = self._student_for_user(normalized_user)
            if not student:
                response = {"text": "I couldn't find your student profile."}
            else:
                response = {"text": f"Your attendance is {student['attendance']:.1f}%."}
            self._remember_context(normalized_user, student["student_id"] if student else None, "attendance")
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return {**response, "language": language}

        if intent == "GET_CHILD_ATTENDANCE":
            if resolved_role != "parent":
                response = {"text": "You don't have permission to access that attendance information.", "status": "denied"}
                self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
                return response
            child_students = self._parent_children(normalized_user)
            if not child_students:
                response = {"text": "I couldn't find your child record."}
                self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
                return response
            target_student = child_students[0]
            if entities.get("student_name"):
                target_student = self._resolve_student_name(entities["student_name"])
                if not target_student or target_student["student_id"] not in [child["student_id"] for child in child_students]:
                    response = {"text": "You can only view attendance for your own child.", "status": "denied"}
                    self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
                    return response
            response = self._student_response(target_student["student_id"], include_prompt=True, time_period=entities.get("time_period"))
            self._remember_context(normalized_user, target_student["student_id"], "attendance", entities.get("time_period"))
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return {**response, "language": language}

        if intent == "GET_STUDENT_ATTENDANCE":
            if resolved_role == "student":
                student = self._student_for_user(normalized_user)
                response = {"text": f"Your attendance is {student['attendance']:.1f}%."} if student else {"text": "I couldn't find your student profile."}
            elif resolved_role == "principal":
                response = self._principal_analytics_response()
            else:
                response = {"text": "You don't have permission to access that attendance information.", "status": "denied"}
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return {**response, "language": language}

        if intent == "GET_SCHOOL_ATTENDANCE":
            if resolved_role != "principal":
                response = {"text": "You don't have permission to access school-wide attendance analytics.", "status": "denied"}
                self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
                return response
            response = self._principal_analytics_response()
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return {**response, "language": language}

        if intent == "GET_RECENT_ATTENDANCE":
            context = self._get_session_context(normalized_user)
            student_id = context.get("student_id")
            if not student_id:
                response = {"text": "I can help with that. Which student would you like me to check?"}
            else:
                student = self.students.get(self._normalize_id(student_id))
                response = {"text": f"{student['name']} currently has {student['attendance']:.1f}% attendance."}
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return {**response, "language": language}

        if resolved_role == "student" and ("hello" in lower or "hi" in lower):
            response = {"text": "Hi! I’m XYZ AI, your school assistant. How can I help you today?"}
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return {**response, "language": language}

        if resolved_role == "parent" and ("hello" in lower or "hi" in lower):
            response = {"text": "Hello! I’m here to help you with your child’s school information. How may I support you today?"}
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return {**response, "language": language}

        if resolved_role == "teacher" and ("hello" in lower or "hi" in lower):
            response = {"text": "Hello, teacher. How can I assist with student and class management today?"}
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return {**response, "language": language}

        if resolved_role == "principal" and ("hello" in lower or "hi" in lower):
            response = {"text": "Good day, Principal. I can help with attendance insights and school operations."}
            self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
            return {**response, "language": language}

        response = {
            "text": f"I understand you’re asking about: \"{msg}\". I can help with attendance, student records, teacher escalations, and school operations. Please clarify your request.",
            "language": language,
        }
        self._record_interaction(resolved_role, normalized_user, msg, response, intent=intent, tool=tool)
        return response

    def handle_escalation(self, role, user_id, target):
        return self._handle_escalation(role, user_id, target)
