"""
Attendance service - handles all attendance-related operations.
"""

from datetime import datetime


class AttendanceService:
    """Manages attendance operations for students."""

    # Mock attendance data
    ATTENDANCE_DATA = {
        "S001": {
            "student_id": "S001",
            "student_name": "Rahul Sharma",
            "current_percentage": 91.2,
            "total_days": 150,
            "present_days": 137,
            "absent_days": 13,
            "records": [
                {"date": "2026-08-15", "status": "present"},
                {"date": "2026-08-14", "status": "present"},
                {"date": "2026-08-13", "status": "absent"},
                {"date": "2026-08-12", "status": "present"},
                {"date": "2026-08-11", "status": "present"},
            ],
        },
        "S002": {
            "student_id": "S002",
            "student_name": "Rohan Verma",
            "current_percentage": 87.5,
            "total_days": 150,
            "present_days": 131,
            "absent_days": 19,
            "records": [
                {"date": "2026-08-15", "status": "present"},
                {"date": "2026-08-14", "status": "absent"},
                {"date": "2026-08-13", "status": "present"},
                {"date": "2026-08-12", "status": "present"},
                {"date": "2026-08-11", "status": "absent"},
            ],
        },
        "S003": {
            "student_id": "S003",
            "student_name": "Priya Singh",
            "current_percentage": 94.1,
            "total_days": 150,
            "present_days": 141,
            "absent_days": 9,
            "records": [
                {"date": "2026-08-15", "status": "present"},
                {"date": "2026-08-14", "status": "present"},
                {"date": "2026-08-13", "status": "present"},
                {"date": "2026-08-12", "status": "present"},
                {"date": "2026-08-11", "status": "present"},
            ],
        },
    }

    SCHOOL_ATTENDANCE = {
        "school_id": "SCHOOL001",
        "date": "2026-08-15",
        "total_students": 1240,
        "present_students": 1113,
        "absent_students": 127,
        "overall_percentage": 89.7,
        "class_wise": {
            "10A": {"total": 45, "present": 41, "percentage": 91.1},
            "10B": {"total": 48, "present": 42, "percentage": 87.5},
            "9A": {"total": 46, "present": 42, "percentage": 91.3},
            "9B": {"total": 47, "present": 40, "percentage": 85.1},
        },
    }

    def get_student_attendance(self, student_id):
        """Get attendance record for a student."""
        if student_id in self.ATTENDANCE_DATA:
            return self.ATTENDANCE_DATA[student_id].copy()
        return None

    def mark_attendance(self, student_id, date, status):
        """
        Mark attendance for a student.
        
        Args:
            student_id: Student ID
            date: Date string (YYYY-MM-DD) or "today"
            status: "present", "absent", or "leave"
            
        Returns:
            Updated attendance record or None if failed
        """
        if student_id not in self.ATTENDANCE_DATA:
            return None

        if status not in ["present", "absent", "leave"]:
            return None

        student_record = self.ATTENDANCE_DATA[student_id]
        
        # Convert "today" to actual date
        if date == "today":
            date = datetime.now().strftime("%Y-%m-%d")

        # Find or create record for date
        existing_idx = None
        for idx, record in enumerate(student_record["records"]):
            if record["date"] == date:
                existing_idx = idx
                break

        if existing_idx is not None:
            student_record["records"][existing_idx]["status"] = status
        else:
            student_record["records"].insert(0, {"date": date, "status": status})

        # Recalculate percentages
        present = sum(1 for r in student_record["records"] if r["status"] == "present")
        total = len(student_record["records"])
        student_record["present_days"] = present
        student_record["total_days"] = total
        if total > 0:
            student_record["current_percentage"] = round((present / total) * 100, 1)

        return student_record.copy()

    def get_school_attendance(self):
        """Get overall school attendance statistics."""
        return self.SCHOOL_ATTENDANCE.copy()

    def get_recent_attendance(self, student_id, days=7):
        """Get recent attendance records for a student."""
        if student_id not in self.ATTENDANCE_DATA:
            return None

        student_record = self.ATTENDANCE_DATA[student_id]
        recent = student_record["records"][:days]
        
        return {
            "student_id": student_id,
            "student_name": student_record["student_name"],
            "recent_records": recent,
            "current_percentage": student_record["current_percentage"],
        }

    def get_attendance_for_students(self, student_ids):
        """Get attendance for multiple students."""
        result = {}
        for sid in student_ids:
            if sid in self.ATTENDANCE_DATA:
                result[sid] = self.ATTENDANCE_DATA[sid].copy()
        return result

