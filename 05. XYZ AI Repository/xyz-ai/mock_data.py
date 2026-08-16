"""
Mock school data repository.
Provides consistent, unified data structures for all school entities.
"""


class MockSchoolDatabase:
    """Centralized mock data for the school system."""

    def __init__(self):
        """Initialize all mock data with proper relationships."""
        # Students with consistent attendance data
        self.students = {
            "S001": {
                "student_id": "S001",
                "name": "Rahul Sharma",
                "class": "Grade 10-A",
                "section": "A",
                "parent_id": "P001",
                "teacher_id": "T001",
                "attendance": 91.2,
                "attendance_percentage": 91.2,
                "total_days": 150,
                "present_days": 137,
                "absent_days": 13,
            },
            "S002": {
                "student_id": "S002",
                "name": "Rohan Verma",
                "class": "Grade 10-A",
                "section": "A",
                "parent_id": "P002",
                "teacher_id": "T001",
                "attendance": 87.5,
                "attendance_percentage": 87.5,
                "total_days": 150,
                "present_days": 131,
                "absent_days": 19,
            },
            "S003": {
                "student_id": "S003",
                "name": "Priya Singh",
                "class": "Grade 10-B",
                "section": "B",
                "parent_id": "P003",
                "teacher_id": "T002",
                "attendance": 94.1,
                "attendance_percentage": 94.1,
                "total_days": 150,
                "present_days": 141,
                "absent_days": 9,
            },
        }

        # Parents with child-parent relationships
        self.parents = {
            "P001": {
                "parent_id": "P001",
                "name": "Priya Sharma",
                "email": "priya.parent@school.edu",
                "child_ids": ["S001"],  # Can only access S001
                "phone": "9876543210",
            },
            "P002": {
                "parent_id": "P002",
                "name": "Amit Verma",
                "email": "amit.parent@school.edu",
                "child_ids": ["S002"],
                "phone": "9876543211",
            },
            "P003": {
                "parent_id": "P003",
                "name": "Neha Singh",
                "email": "neha.parent@school.edu",
                "child_ids": ["S003"],
                "phone": "9876543212",
            },
        }

        # Teachers with authorized student lists
        self.teachers = {
            "T001": {
                "teacher_id": "T001",
                "name": "Anita Gupta",
                "email": "anita@school.edu",
                "subject": "Mathematics",
                "authorized_student_ids": ["S001", "S002"],  # Can mark attendance only for these
                "phone": "9876543220",
            },
            "T002": {
                "teacher_id": "T002",
                "name": "Vikram Singh",
                "email": "vikram@school.edu",
                "subject": "English",
                "authorized_student_ids": ["S003"],
                "phone": "9876543221",
            },
        }

        # Principals / School Management
        self.principals = {
            "PR001": {
                "principal_id": "PR001",
                "name": "Raj Mehta",
                "email": "raj@school.edu",
                "school_id": "SCHOOL001",
                "phone": "9876543230",
            },
        }

        # School metadata
        self.school = {
            "school_id": "SCHOOL001",
            "name": "XYZ School of Excellence",
            "overall_attendance": 89.7,
            "total_students": 1240,
            "total_teachers": 68,
            "total_parents": 980,
            "city": "Delhi",
            "country": "India",
            "language_support": ["en", "hi", "ta", "te", "mr", "bn", "gu", "pa", "kn", "ml", "ur"],
        }

        # Demo user mapping (for UI selection)
        self.demo_users = {
            "student_1": "S001",
            "student_2": "S002",
            "student_3": "S003",
            "parent_1": "P001",
            "parent_2": "P002",
            "parent_3": "P003",
            "teacher_1": "T001",
            "teacher_2": "T002",
            "principal_1": "PR001",
        }

    def get_student(self, student_id):
        """Get student by ID."""
        normalized = self._normalize_id(student_id)
        return self.students.get(normalized)

    def get_parent(self, parent_id):
        """Get parent by ID."""
        normalized = self._normalize_id(parent_id)
        return self.parents.get(normalized)

    def get_teacher(self, teacher_id):
        """Get teacher by ID."""
        normalized = self._normalize_id(teacher_id)
        return self.teachers.get(normalized)

    def get_principal(self, principal_id):
        """Get principal by ID."""
        normalized = self._normalize_id(principal_id)
        return self.principals.get(normalized)

    def get_parent_children(self, parent_id):
        """Get all children of a parent."""
        parent = self.get_parent(parent_id)
        if not parent:
            return []
        children = []
        for child_id in parent.get("child_ids", []):
            student = self.get_student(child_id)
            if student:
                children.append(student)
        return children

    def get_all_students(self):
        """Get all students."""
        return list(self.students.values())

    def get_school_stats(self):
        """Get school-wide statistics."""
        return self.school.copy()

    def _normalize_id(self, value):
        """Normalize ID: resolve demo user IDs to real IDs."""
        if value is None:
            return None
        text = str(value).strip()
        # Resolve demo IDs
        if text in self.demo_users:
            return self.demo_users[text]
        # Resolve case-insensitive IDs
        mapping = {
            "s001": "S001",
            "s002": "S002",
            "s003": "S003",
            "p001": "P001",
            "p002": "P002",
            "p003": "P003",
            "t001": "T001",
            "pr001": "PR001",
        }
        return mapping.get(text.lower(), text)

    def resolve_user_id(self, user_id):
        """Resolve any user ID format to canonical form."""
        return self._normalize_id(user_id)

    def get_user_role(self, user_id):
        """Determine the role of a user based on their ID."""
        normalized = self._normalize_id(user_id)
        if normalized in self.students:
            return "student"
        if normalized in self.parents:
            return "parent"
        if normalized in self.teachers:
            return "teacher"
        if normalized in self.principals:
            return "principal"
        return None
