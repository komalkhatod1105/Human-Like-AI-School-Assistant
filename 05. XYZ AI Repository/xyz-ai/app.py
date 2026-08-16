"""
XYZ AI School Assistant - Flask Application
Main entry point for the application.
"""
from flask import Flask, jsonify, request, render_template, session
from functools import wraps
import os
from auth_service import AuthenticationService
from intent_service import Intent
from attendance_service import AttendanceService
from support_service import SupportService
from conversation_memory import ConversationMemoryStore
from mock_data import MockSchoolDatabase
from language_service import LanguageService
from services import SchoolAssistantService


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__, template_folder="templates", static_folder="templates/static")
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Initialize services
    auth_service = AuthenticationService()
    attendance_service = AttendanceService()
    support_service = SupportService()
    memory_store = ConversationMemoryStore()
    db = MockSchoolDatabase()
    language_service = LanguageService()
    school_assistant = SchoolAssistantService()  # Main AI service orchestrator

    # Middleware to verify authentication
    def require_auth(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            payload = request.get_json(silent=True) or {}
            user_id = payload.get("user_id")
            if not user_id:
                return jsonify({"error": "Missing user_id"}), 400
            return f(*args, **kwargs)
        return decorated_function

    # ============ FRONTEND ROUTES ============

    @app.route("/", methods=["GET"])
    def index():
        """Serve main application."""
        return render_template("index.html")

    @app.route("/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "ok", "service": "xyz-ai-school-assistant"})

    # ============ AUTHENTICATION ROUTES ============

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        """Authenticate user and establish session."""
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")

        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        # Authenticate user - backend determines role
        user_info = auth_service.get_authenticated_user(user_id)
        if not user_info:
            return jsonify({"error": "User not found"}), 401

        # Store in session
        session["user_id"] = user_info["user_id"]
        session["role"] = user_info["role"]

        return jsonify(user_info), 200

    @app.route("/api/auth/logout", methods=["POST"])
    def logout():
        """Logout user."""
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")
        if user_id:
            memory_store.clear(user_id)
        session.clear()
        return jsonify({"status": "logged_out"}), 200

    @app.route("/api/auth/users", methods=["GET"])
    def get_available_users():
        """Get list of available demo users for testing."""
        users = {
            "students": [
                {"id": "S001", "name": "Rahul Sharma"},
                {"id": "S002", "name": "Rohan Verma"},
                {"id": "S003", "name": "Priya Singh"},
            ],
            "parents": [
                {"id": "P001", "name": "Priya Sharma", "children": ["Rahul Sharma"]},
                {"id": "P002", "name": "Amit Verma", "children": ["Rohan Verma"]},
                {"id": "P003", "name": "Neha Singh", "children": ["Priya Singh"]},
            ],
            "teachers": [
                {"id": "T001", "name": "Anita Gupta", "subject": "Mathematics"},
                {"id": "T002", "name": "Vikram Singh", "subject": "English"},
            ],
            "principals": [
                {"id": "PR001", "name": "Raj Mehta"},
            ],
        }
        return jsonify(users), 200

    # ============ CHAT ROUTES ============

    @app.route("/api/chat", methods=["POST"])
    @require_auth
    def chat():
        """Main chat endpoint - processes user messages and generates AI responses."""
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")
        message = payload.get("message", "").strip()
        language = payload.get("language", "en")

        if not message:
            return jsonify({"text": "How can I help you today?", "language": language}), 200

        # Use SchoolAssistantService to process the message
        # This service handles intent detection, authorization, and response generation
        response = school_assistant.process_message(user_id, message, language=language)

        return jsonify(response), 200

    # ============ ATTENDANCE ROUTES ============

    @app.route("/api/attendance/my", methods=["POST"])
    @require_auth
    def get_my_attendance():
        """Get authenticated user's own attendance (student only)."""
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")

        user_info = auth_service.get_authenticated_user(user_id)
        if not user_info or user_info["role"] != "student":
            return jsonify({"error": "Unauthorized"}), 403

        attendance = attendance_service.get_student_attendance(user_id)
        if not attendance:
            return jsonify({"error": "Attendance record not found"}), 404

        return jsonify(attendance), 200

    @app.route("/api/attendance/student/<student_id>", methods=["POST"])
    @require_auth
    def get_student_attendance_auth(student_id):
        """Get a student's attendance (authorized users only)."""
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")

        user_info = auth_service.get_authenticated_user(user_id)
        if not user_info:
            return jsonify({"error": "Unauthorized"}), 403

        role = user_info["role"]

        # Check authorization
        if role == "student":
            # Student can only view own
            if user_id != student_id:
                return jsonify({"error": "You can only view your own attendance"}), 403
        elif role == "parent":
            # Parent can only view child's
            if "child_ids" not in user_info or student_id not in user_info.get("child_ids", []):
                return jsonify({"error": "You don't have access to this student"}), 403
        elif role == "teacher":
            # Teacher can only view authorized students
            if student_id not in user_info.get("authorized_student_ids", []):
                return jsonify({"error": "You are not authorized for this student"}), 403
        elif role != "principal":
            # Only principal has universal access
            return jsonify({"error": "Unauthorized"}), 403

        attendance = attendance_service.get_student_attendance(student_id)
        if not attendance:
            return jsonify({"error": "Attendance record not found"}), 404

        return jsonify(attendance), 200

    @app.route("/api/attendance/mark", methods=["POST"])
    @require_auth
    def mark_attendance():
        """Mark student attendance (teachers only)."""
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")
        student_id = payload.get("student_id")
        date = payload.get("date", "today")
        status = payload.get("status")

        user_info = auth_service.get_authenticated_user(user_id)
        if not user_info or user_info["role"] != "teacher":
            return jsonify({"error": "Only teachers can mark attendance"}), 403

        # Check teacher is authorized for this student
        if student_id not in user_info.get("authorized_student_ids", []):
            return jsonify({"error": "You are not authorized to mark attendance for this student"}), 403

        if status not in ["present", "absent", "leave"]:
            return jsonify({"error": "Invalid attendance status"}), 400

        result = attendance_service.mark_attendance(student_id, date, status)
        if not result:
            return jsonify({"error": "Failed to mark attendance"}), 500

        return jsonify({
            "success": True,
            "student_id": student_id,
            "status": status,
            "date": date,
            "message": f"Marked {result['student_name']} as {status}",
        }), 200

    # ============ ANALYTICS ROUTES ============

    @app.route("/api/analytics/school", methods=["POST"])
    @require_auth
    def get_school_analytics():
        """Get school-wide attendance analytics (principals only)."""
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")

        user_info = auth_service.get_authenticated_user(user_id)
        if not user_info or user_info["role"] != "principal":
            return jsonify({"error": "Only principals can access school analytics"}), 403

        analytics = attendance_service.get_school_attendance()
        return jsonify(analytics), 200

    # ============ SUPPORT/ESCALATION ROUTES ============

    @app.route("/api/support/teacher-request", methods=["POST"])
    @require_auth
    def request_teacher_call():
        """Request teacher call (parents only)."""
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")
        student_id = payload.get("student_id")
        reason = payload.get("reason")

        user_info = auth_service.get_authenticated_user(user_id)
        if not user_info or user_info["role"] != "parent":
            return jsonify({"error": "Only parents can request teacher calls"}), 403

        # Verify student is parent's child
        if student_id not in user_info.get("child_ids", []):
            return jsonify({"error": "This student is not your child"}), 403

        request_data = support_service.create_teacher_call_request(user_id, student_id, reason)
        return jsonify(request_data), 200

    @app.route("/api/support/management-request", methods=["POST"])
    @require_auth
    def request_management_call():
        """Request management call (parents/teachers)."""
        payload = request.get_json(silent=True) or {}
        user_id = payload.get("user_id")
        reason = payload.get("reason")

        user_info = auth_service.get_authenticated_user(user_id)
        if not user_info or user_info["role"] not in ["parent", "teacher"]:
            return jsonify({"error": "Only parents and teachers can request management"}), 403

        request_data = support_service.create_management_call_request(user_id, user_info["role"], reason)
        return jsonify(request_data), 200

    # ============ UTILITY ROUTES ============

    @app.route("/api/students/<student_id>", methods=["GET"])
    def get_student_info(student_id):
        """Get student information."""
        student = db.get_student(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        return jsonify(student), 200

    @app.route("/api/parents/<parent_id>/children", methods=["GET"])
    def get_parent_children(parent_id):
        """Get children of a parent."""
        children = db.get_parent_children(parent_id)
        if not children:
            return jsonify({"error": "No children found"}), 404
        return jsonify({"children": children}), 200

    return app


def process_intent(intent, role, user_id, message, user_info, intent_service, 
                   attendance_service, support_service, memory_store, db, 
                   language_service, language):
    """Process detected intent and generate appropriate response."""

    if intent == Intent.GET_OWN_ATTENDANCE:
        student = db.get_student(user_id)
        if not student:
            return "I couldn't find your attendance record."
        attendance = attendance_service.get_student_attendance(user_id)
        if not attendance:
            return "I couldn't find your attendance record."
        pct = attendance.get("current_percentage", 0)
        return f"Your current attendance is {pct}%. Keep it up!"

    elif intent == Intent.GET_CHILD_ATTENDANCE:
        parent_children = db.get_parent_children(user_id)
        if not parent_children:
            return "I couldn't find your child's record."
        
        # Try to find mentioned child from message
        student_name = intent_service._extract_student_name(message.lower())
        target_child = None
        if student_name:
            for child in parent_children:
                if child["name"].lower() == student_name.lower():
                    target_child = child
                    break
        
        if not target_child and len(parent_children) == 1:
            target_child = parent_children[0]
        
        if not target_child:
            names = ", ".join([c["name"] for c in parent_children])
            return f"Which child? I know about: {names}"
        
        attendance = attendance_service.get_student_attendance(target_child["student_id"])
        if not attendance:
            return f"I couldn't find {target_child['name']}'s attendance record."
        
        pct = attendance.get("current_percentage", 0)
        memory_store.update_context(user_id, "mentioned_student_id", target_child["student_id"])
        memory_store.update_context(user_id, "mentioned_student_name", target_child["name"])
        
        return f"{target_child['name']} currently has {pct}% attendance. Would you like more details?"

    elif intent == Intent.MARK_ATTENDANCE:
        student_name = intent_service._extract_student_name(message.lower())
        status = intent_service._extract_attendance_status(message.lower())
        
        if not student_name:
            return "Which student should I mark attendance for?"
        if not status:
            return "Should I mark them present, absent, or on leave?"
        
        student_obj = intent_service.resolve_student_by_name(student_name)
        if not student_obj:
            return f"I couldn't find a student named {student_name}."
        
        # This will be done via the attendance API endpoint which checks authorization
        return f"Ready to mark {student_name} as {status}. Please confirm via the API."

    elif intent == Intent.GET_SCHOOL_ATTENDANCE:
        analytics = attendance_service.get_school_attendance()
        overall = analytics.get("overall_percentage", 0)
        total = analytics.get("total_students", 0)
        return f"The overall school attendance is {overall}% across {total} students. How can I help further?"

    elif intent == Intent.REQUEST_TEACHER_CALL:
        context = memory_store.get_context(user_id)
        child_id = context.get("mentioned_student_id") if context else None
        
        if not child_id:
            children = db.get_parent_children(user_id)
            if len(children) == 1:
                child_id = children[0]["student_id"]
            else:
                child_names = ", ".join([c["name"] for c in children])
                return f"For which child? {child_names}"
        
        return f"I can submit a teacher call request for you. Would you like me to proceed? Say 'Yes' to confirm."

    elif intent == Intent.REQUEST_MANAGEMENT_CALL:
        return "I can connect you with school management. Would you like me to submit a request? Say 'Yes' to confirm."

    elif intent == Intent.GENERAL_HELP:
        if role == "student":
            return "I'm your School Assistant! I can check your attendance, answer questions about school, and connect you with teachers or management."
        elif role == "parent":
            return "I'm your School Assistant! I can check your child's attendance, help with school matters, and connect you with teachers or management."
        elif role == "teacher":
            return "I'm your School Assistant! I can help you mark attendance, check student records, and manage escalations."
        elif role == "principal":
            return "I'm your School Assistant! I can show you school analytics, attendance reports, and help with management matters."
        return "How can I help you today?"

    else:
        return "I'm not sure how to help with that. Could you rephrase your question? I can help with attendance, student records, and escalations."


# Create app instance
app = create_app()


if __name__ == "__main__":
    # Bind to 0.0.0.0 and use PORT env variable for production (Render, etc.)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
