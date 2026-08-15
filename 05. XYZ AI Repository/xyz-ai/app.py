from flask import Flask, jsonify, request, render_template
from services import SchoolAssistantService


def create_app():
    app = Flask(__name__)
    service = SchoolAssistantService()

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"})

    @app.route("/api/chat", methods=["POST"])
    def chat():
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "student")
        user_id = payload.get("user_id", "student_1")
        message = payload.get("message", "")
        history = payload.get("history", [])

        response = service.process_message(role, user_id, message, history)
        return jsonify(response)

    @app.route("/api/escalate", methods=["POST"])
    def escalate():
        payload = request.get_json(silent=True) or {}
        role = payload.get("role", "parent")
        user_id = payload.get("user_id", "parent_1")
        target = payload.get("target", "teacher")
        request_id = payload.get("request_id")

        result = service.handle_escalation(role, user_id, target, request_id)
        return jsonify(result)

    @app.route("/api/students/<student_id>", methods=["GET"])
    def student_detail(student_id):
        result = service.get_student(student_id)
        return jsonify(result)

    @app.route("/api/students/<student_id>/attendance", methods=["GET"])
    def student_attendance(student_id):
        result = service.get_student_attendance(student_id)
        return jsonify(result)

    @app.route("/api/parents/<parent_id>/children", methods=["GET"])
    def parent_children(parent_id):
        result = service.get_parent_children(parent_id)
        return jsonify(result)

    @app.route("/api/attendance/mark", methods=["POST"])
    def attendance_mark():
        payload = request.get_json(silent=True) or {}
        result = service.mark_attendance_api(
            payload.get("student_id"),
            payload.get("date") or "today",
            payload.get("status") or "present",
            payload.get("teacher_id"),
        )
        return jsonify(result)

    @app.route("/api/analytics/attendance", methods=["GET"])
    def school_analytics():
        result = service.get_school_analytics()
        return jsonify(result)

    @app.route("/api/support/call-request", methods=["POST"])
    def support_call_request():
        payload = request.get_json(silent=True) or {}
        result = service.submit_support_request(
            payload.get("requested_by"),
            payload.get("target_type", "teacher"),
            payload.get("student_id"),
            payload.get("reason", "School support request"),
        )
        return jsonify(result)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
