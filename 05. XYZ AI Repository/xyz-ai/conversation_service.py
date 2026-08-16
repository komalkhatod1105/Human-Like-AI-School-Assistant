"""
Conversation memory and context management.
Maintains per-user conversation state and context.
"""
from datetime import datetime, timezone


class ConversationService:
    """Manages per-user conversation state and context."""

    def __init__(self):
        """Initialize conversation service."""
        self.sessions = {}
        self.conversation_log = []

    def get_or_create_session(self, user_id):
        """Get or create a conversation session for a user."""
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "user_id": user_id,
                "messages": [],
                "context": {},
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        return self.sessions[user_id]

    def add_message(self, user_id, role, text):
        """Add a message to the conversation."""
        session = self.get_or_create_session(user_id)
        message = {
            "role": role,
            "text": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        session["messages"].append(message)
        return message

    def update_context(self, user_id, context_updates):
        """Update the conversation context."""
        session = self.get_or_create_session(user_id)
        session["context"].update(context_updates)

    def get_context(self, user_id):
        """Get the current conversation context."""
        session = self.get_or_create_session(user_id)
        return session.get("context", {})

    def remember_student(self, user_id, student_id, student_name=None):
        """Remember a student in the conversation context."""
        context = self.get_context(user_id)
        context["current_student_id"] = student_id
        if student_name:
            context["current_student_name"] = student_name
        self.update_context(user_id, context)

    def get_remembered_student(self, user_id):
        """Get the currently remembered student in conversation."""
        context = self.get_context(user_id)
        return {
            "student_id": context.get("current_student_id"),
            "student_name": context.get("current_student_name"),
        }

    def remember_topic(self, user_id, topic, details=None):
        """Remember the current topic of conversation."""
        context = self.get_context(user_id)
        context["current_topic"] = topic
        if details:
            context["topic_details"] = details
        self.update_context(user_id, context)

    def get_remembered_topic(self, user_id):
        """Get the current topic of conversation."""
        context = self.get_context(user_id)
        return {
            "topic": context.get("current_topic"),
            "details": context.get("topic_details"),
        }

    def clear_session(self, user_id):
        """Clear a user's session."""
        if user_id in self.sessions:
            del self.sessions[user_id]

    def record_interaction(self, user_id, role, message, response, intent=None, tool=None):
        """Record an interaction for audit/analytics."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "role": role,
            "message": message,
            "response": response.get("text", ""),
            "intent": intent,
            "tool": tool,
            "status": response.get("status", "completed"),
        }
        self.conversation_log.append(record)
        return record

    def get_session_history(self, user_id):
        """Get the message history for a user's session."""
        session = self.get_or_create_session(user_id)
        return session.get("messages", [])
