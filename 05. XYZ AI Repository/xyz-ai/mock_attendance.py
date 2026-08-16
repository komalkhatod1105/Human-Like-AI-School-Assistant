"""
Mock attendance database.
"""

from datetime import datetime, timedelta

# Current attendance records
MOCK_ATTENDANCE = {
    "S001": {  # Rahul
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
    "S002": {  # Rohan
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
    "S003": {  # Priya
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

MOCK_SCHOOL_ATTENDANCE = {
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


def get_student_attendance(student_id):
    """Get attendance for a specific student."""
    if student_id in MOCK_ATTENDANCE:
        return MOCK_ATTENDANCE[student_id].copy()
    return None


def mark_student_attendance(student_id, date, status):
    """Mark attendance for a student. Returns updated record or None."""
    if student_id not in MOCK_ATTENDANCE:
        return None
    
    # Validate status
    if status not in ["present", "absent", "leave"]:
        return None
    
    student_record = MOCK_ATTENDANCE[student_id]
    
    # Add or update record
    date_str = str(date)
    existing = None
    for record in student_record["records"]:
        if record["date"] == date_str:
            existing = record
            break
    
    if existing:
        existing["status"] = status
    else:
        student_record["records"].insert(0, {"date": date_str, "status": status})
    
    # Recalculate percentages
    present = sum(1 for r in student_record["records"] if r["status"] == "present")
    total = len(student_record["records"])
    student_record["present_days"] = present
    student_record["total_days"] = total
    if total > 0:
        student_record["current_percentage"] = round((present / total) * 100, 1)
    
    return student_record.copy()


def get_school_attendance(date=None):
    """Get overall school attendance."""
    return MOCK_SCHOOL_ATTENDANCE.copy()


def get_attendance_by_student_ids(student_ids):
    """Get attendance for multiple students."""
    result = {}
    for sid in student_ids:
        if sid in MOCK_ATTENDANCE:
            result[sid] = MOCK_ATTENDANCE[sid].copy()
    return result
