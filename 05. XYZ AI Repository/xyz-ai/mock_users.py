"""
Mock user database for authentication and role management.
This is a prototype implementation. In production, use a real authentication system.
"""

MOCK_USERS = {
    # STUDENT
    "student_rahul": {
        "user_id": "S001",
        "name": "Rahul Sharma",
        "role": "student",
        "email": "rahul@school.edu",
        "password": "student123",  # Mock only
        "class": "10A",
        "section": "A",
    },
    "student_rohan": {
        "user_id": "S002",
        "name": "Rohan Verma",
        "role": "student",
        "email": "rohan@school.edu",
        "password": "student123",
        "class": "10A",
        "section": "A",
    },
    "student_priya": {
        "user_id": "S003",
        "name": "Priya Singh",
        "role": "student",
        "email": "priya@school.edu",
        "password": "student123",
        "class": "10B",
        "section": "B",
    },
    # PARENT
    "parent_priya": {
        "user_id": "P001",
        "name": "Priya Sharma",
        "role": "parent",
        "email": "priya.parent@school.edu",
        "password": "parent123",
        "child_ids": ["S001"],  # Can view only these children
    },
    "parent_amit": {
        "user_id": "P002",
        "name": "Amit Verma",
        "role": "parent",
        "email": "amit@school.edu",
        "password": "parent123",
        "child_ids": ["S002"],
    },
    # TEACHER
    "teacher_anita": {
        "user_id": "T001",
        "name": "Anita Gupta",
        "role": "teacher",
        "email": "anita@school.edu",
        "password": "teacher123",
        "subject": "Mathematics",
        "authorized_student_ids": ["S001", "S002", "S003"],  # Can modify attendance for these
    },
    "teacher_vikram": {
        "user_id": "T002",
        "name": "Vikram Singh",
        "role": "teacher",
        "email": "vikram@school.edu",
        "password": "teacher123",
        "subject": "English",
        "authorized_student_ids": ["S001", "S002"],
    },
    # PRINCIPAL / SCHOOL MANAGEMENT
    "principal_raj": {
        "user_id": "PR001",
        "name": "Raj Mehta",
        "role": "principal",
        "email": "raj@school.edu",
        "password": "principal123",
        "school_id": "SCHOOL001",
    },
}

MOCK_SCHOOL_INFO = {
    "school_id": "SCHOOL001",
    "name": "XYZ School of Excellence",
    "total_students": 1240,
    "total_teachers": 68,
    "total_parents": 980,
    "overall_attendance": 89.7,
    "city": "Delhi",
    "country": "India",
}

def get_user_by_id(user_id):
    """Get user by user_id or username."""
    # Try direct lookup
    if user_id in MOCK_USERS:
        return MOCK_USERS[user_id].copy()
    # Try by user_id field
    for username, user in MOCK_USERS.items():
        if user.get("user_id") == user_id:
            return user.copy()
    return None


def authenticate_user(username, password):
    """Authenticate user. Returns user data if successful, None otherwise."""
    if username not in MOCK_USERS:
        return None
    user = MOCK_USERS[username].copy()
    if user.get("password") == password:
        user.pop("password", None)  # Remove password from returned data
        return user
    return None


def get_school_info():
    """Get school information."""
    return MOCK_SCHOOL_INFO.copy()
