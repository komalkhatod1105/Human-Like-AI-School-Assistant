"""
Authentication and session management.
Handles user identity verification and role resolution.
"""
from mock_data import MockSchoolDatabase


class AuthenticationService:
    """Manages user authentication and session state."""

    def __init__(self):
        """Initialize authentication service."""
        self.db = MockSchoolDatabase()
        self.sessions = {}

    def authenticate_user(self, user_id):
        """
        Authenticate a user and return their role.
        Backend determines role from user_id, not from user claims.
        """
        if not user_id:
            return None, None

        normalized_id = self.db.resolve_user_id(user_id)
        role = self.db.get_user_role(normalized_id)

        if not role:
            return None, None

        # Create/update session
        self._create_session(normalized_id, role)
        return normalized_id, role

    def get_authenticated_user(self, user_id):
        """Get authenticated user info."""
        normalized_id = self.db.resolve_user_id(user_id)
        role = self.db.get_user_role(normalized_id)

        if not role:
            return None

        user_info = {
            "user_id": normalized_id,
            "role": role,
            "name": self._get_user_name(normalized_id, role),
        }
        
        # Add role-specific data
        if role == "student":
            student = self.db.get_student(normalized_id)
            if student:
                user_info["student_id"] = student.get("student_id")
                user_info["class"] = student.get("class")
        elif role == "parent":
            parent = self.db.get_parent(normalized_id)
            if parent:
                user_info["parent_id"] = parent.get("parent_id")
                user_info["child_ids"] = parent.get("child_ids", [])
        elif role == "teacher":
            teacher = self.db.get_teacher(normalized_id)
            if teacher:
                user_info["teacher_id"] = teacher.get("teacher_id")
                user_info["authorized_student_ids"] = teacher.get("authorized_student_ids", [])
        elif role == "principal":
            principal = self.db.get_principal(normalized_id)
            if principal:
                user_info["principal_id"] = principal.get("principal_id")
        
        return user_info

    def _create_session(self, user_id, role):
        """Create or update a user session."""
        self.sessions[user_id] = {
            "user_id": user_id,
            "role": role,
            "context": {},
        }

    def _get_user_name(self, user_id, role):
        """Get the display name for a user."""
        if role == "student":
            student = self.db.get_student(user_id)
            return student["name"] if student else "Student"
        elif role == "parent":
            parent = self.db.get_parent(user_id)
            return parent["name"] if parent else "Parent"
        elif role == "teacher":
            teacher = self.db.get_teacher(user_id)
            return teacher["name"] if teacher else "Teacher"
        elif role == "principal":
            principal = self.db.get_principal(user_id)
            return principal["name"] if principal else "Principal"
        return "User"

    def can_perform_action(self, user_id, action, resource_id=None):
        """
        Check if a user can perform an action.
        Authorization is enforced at backend level.
        """
        normalized_id = self.db.resolve_user_id(user_id)
        role = self.db.get_user_role(normalized_id)

        if not role:
            return False

        # Student permissions
        if role == "student":
            if action == "view_own_attendance":
                return True
            if action == "view_other_attendance":
                return False
            if action == "mark_attendance":
                return False
            if action == "view_school_analytics":
                return False
            return False

        # Parent permissions
        if role == "parent":
            if action == "view_own_attendance":
                return False
            if action == "view_child_attendance":
                # Verify child relationship
                if not resource_id:
                    return False
                children = self.db.get_parent_children(normalized_id)
                child_ids = [c["student_id"] for c in children]
                return resource_id in child_ids
            if action == "mark_attendance":
                return False
            if action == "view_school_analytics":
                return False
            if action == "submit_teacher_request":
                return True
            if action == "submit_management_request":
                return True
            return False

        # Teacher permissions
        if role == "teacher":
            if action == "mark_attendance":
                # Verify student is in authorized list
                if not resource_id:
                    return False
                teacher = self.db.get_teacher(normalized_id)
                return resource_id in teacher.get("authorized_student_ids", [])
            if action == "view_own_attendance":
                return False
            if action == "view_school_analytics":
                return False
            if action == "submit_management_request":
                return True
            return True

        # Principal permissions
        if role == "principal":
            if action == "view_school_analytics":
                return True
            if action == "mark_attendance":
                return True
            return True

        return False
