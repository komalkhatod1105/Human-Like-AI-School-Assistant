"""
Support service - handles escalations and support requests.
"""

from datetime import datetime


class SupportService:
    """Manages support requests and escalations."""

    def __init__(self):
        """Initialize support service."""
        self.requests = {}  # request_id -> request data
        self.request_counter = 1000

    def create_teacher_call_request(self, parent_id, student_id, reason=None):
        """
        Create a teacher call request from a parent.
        
        Args:
            parent_id: Parent ID
            student_id: Student ID
            reason: Reason for request
            
        Returns:
            Request data with request_id
        """
        self.request_counter += 1
        request_id = f"REQ-{self.request_counter}"
        
        request_data = {
            "request_id": request_id,
            "type": "teacher_call",
            "created_by": parent_id,
            "created_by_type": "parent",
            "student_id": student_id,
            "reason": reason or "Parent requested teacher assistance",
            "status": "SUBMITTED",
            "created_at": datetime.now().isoformat(),
        }
        
        self.requests[request_id] = request_data
        return request_data

    def create_management_call_request(self, user_id, user_type, reason=None):
        """
        Create a management/principal escalation request.
        
        Args:
            user_id: User ID requesting escalation
            user_type: "parent" or "teacher"
            reason: Reason for request
            
        Returns:
            Request data with request_id
        """
        self.request_counter += 1
        request_id = f"REQ-{self.request_counter}"
        
        request_data = {
            "request_id": request_id,
            "type": "management_call",
            "created_by": user_id,
            "created_by_type": user_type,
            "reason": reason or f"{user_type.capitalize()} requested management assistance",
            "status": "SUBMITTED",
            "created_at": datetime.now().isoformat(),
        }
        
        self.requests[request_id] = request_data
        return request_data

    def get_request(self, request_id):
        """Get a support request by ID."""
        return self.requests.get(request_id)

    def list_requests(self, user_id=None):
        """List support requests (optionally filtered by user)."""
        if user_id:
            return [r for r in self.requests.values() if r.get("created_by") == user_id]
        return list(self.requests.values())

    def submit_escalation_request(self, user_id, target_type, student_id=None, reason=None):
        """
        Submit an escalation request.
        
        Args:
            user_id: User ID requesting escalation
            target_type: "teacher" or "management"
            student_id: Optional student ID (for parent escalations)
            reason: Reason for escalation
            
        Returns:
            Request data with request_id and success status
        """
        self.request_counter += 1
        request_id = f"REQ-{self.request_counter}"
        
        if target_type == "teacher":
            request_data = {
                "request_id": request_id,
                "type": "teacher_call",
                "created_by": user_id,
                "student_id": student_id,
                "reason": reason or "User requested teacher assistance",
                "status": "SUBMITTED",
                "created_at": datetime.now().isoformat(),
                "success": True,
            }
        elif target_type == "management":
            request_data = {
                "request_id": request_id,
                "type": "management_call",
                "created_by": user_id,
                "reason": reason or "User requested management assistance",
                "status": "SUBMITTED",
                "created_at": datetime.now().isoformat(),
                "success": True,
            }
        else:
            return {
                "success": False,
                "error": f"Invalid target type: {target_type}"
            }
        
        self.requests[request_id] = request_data
        return request_data
