"""
Conversation memory service for maintaining context within a session.
Each user/session has isolated conversation memory.
"""

from datetime import datetime, timedelta


class ConversationMemory:
    """Maintains conversation context for a single user session."""

    def __init__(self, user_id, max_history=20):
        """
        Initialize conversation memory for a user.
        
        Args:
            user_id: The authenticated user's ID
            max_history: Maximum number of messages to keep in memory
        """
        self.user_id = user_id
        self.max_history = max_history
        self.messages = []  # List of {"role": "user"|"assistant", "content": "...", "timestamp": ...}
        self.context = {  # Extracted context from conversation
            "mentioned_student_id": None,
            "mentioned_student_name": None,
            "current_topic": None,  # e.g., "attendance", "escalation"
            "time_period": None,  # e.g., "today", "last month"
            "target_date": None,
        }
        self.created_at = datetime.now()

    def add_message(self, role, content):
        """Add a message to conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
        })
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

    def set_context(self, key, value):
        """Set a context value (e.g., mentioned student)."""
        if key in self.context:
            self.context[key] = value

    def get_context(self, key):
        """Get a context value."""
        return self.context.get(key)

    def update_student_context(self, student_id, student_name):
        """Update the student context for this conversation."""
        self.context["mentioned_student_id"] = student_id
        self.context["mentioned_student_name"] = student_name

    def get_student_context(self):
        """Get currently mentioned student."""
        return {
            "student_id": self.context.get("mentioned_student_id"),
            "student_name": self.context.get("mentioned_student_name"),
        }

    def clear_student_context(self):
        """Clear student context (for topic changes)."""
        self.context["mentioned_student_id"] = None
        self.context["mentioned_student_name"] = None

    def get_recent_messages(self, count=5):
        """Get recent messages for context."""
        return self.messages[-count:]

    def get_full_history(self):
        """Get full conversation history."""
        return self.messages.copy()

    def is_expired(self, timeout_minutes=30):
        """Check if conversation has timed out."""
        age = datetime.now() - self.created_at
        return age > timedelta(minutes=timeout_minutes)

    def reset(self):
        """Clear conversation history and context."""
        self.messages = []
        self.context = {
            "mentioned_student_id": None,
            "mentioned_student_name": None,
            "current_topic": None,
            "time_period": None,
            "target_date": None,
        }
        self.created_at = datetime.now()


class ConversationMemoryStore:
    """Stores conversation memory for multiple user sessions."""

    def __init__(self, timeout_minutes=30):
        """
        Initialize conversation memory store.
        
        Args:
            timeout_minutes: Conversation timeout duration
        """
        self.conversations = {}  # user_id -> ConversationMemory
        self.timeout_minutes = timeout_minutes

    def get_or_create(self, user_id):
        """Get existing conversation or create new one."""
        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationMemory(user_id)
        
        conv = self.conversations[user_id]
        
        # Reset if expired
        if conv.is_expired(self.timeout_minutes):
            conv.reset()
        
        return conv

    def add_user_message(self, user_id, content):
        """Add user message to conversation."""
        conv = self.get_or_create(user_id)
        conv.add_message("user", content)

    def add_assistant_message(self, user_id, content):
        """Add assistant message to conversation."""
        conv = self.get_or_create(user_id)
        conv.add_message("assistant", content)

    def get_context(self, user_id):
        """Get conversation context for a user."""
        conv = self.conversations.get(user_id)
        if not conv:
            return None
        return conv.context.copy()

    def update_context(self, user_id, key, value):
        """Update conversation context."""
        conv = self.get_or_create(user_id)
        conv.set_context(key, value)

    def clear(self, user_id):
        """Clear conversation for a user."""
        if user_id in self.conversations:
            del self.conversations[user_id]
