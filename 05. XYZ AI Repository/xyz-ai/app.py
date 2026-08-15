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

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
