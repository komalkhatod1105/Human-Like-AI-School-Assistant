"""
School analytics service for administrative data.
Provides school-wide statistics and insights.
"""
from mock_data import MockSchoolDatabase


class AnalyticsService:
    """Provides school-wide analytics and statistics."""

    def __init__(self):
        """Initialize analytics service."""
        self.db = MockSchoolDatabase()

    def get_school_attendance_stats(self):
        """
        Get school-wide attendance statistics.
        Only principals and authorized management should access this.
        """
        stats = self.db.get_school_stats()
        return {
            "success": True,
            "overall_attendance": stats["overall_attendance"],
            "total_students": stats["total_students"],
            "total_teachers": stats["total_teachers"],
            "total_parents": stats["total_parents"],
        }

    def can_view_school_analytics(self, user_id):
        """
        Check if a user can view school analytics.
        Only principals can view this.
        """
        normalized_user = self.db.resolve_user_id(user_id)
        role = self.db.get_user_role(normalized_user)
        return role == "principal"

    def get_class_attendance_stats(self):
        """
        Get attendance statistics by class.
        Only principals can access this.
        """
        # Mock data: return class-wise attendance
        return {
            "success": True,
            "classes": [
                {"class": "Grade 9-A", "attendance": 91.2, "students": 35},
                {"class": "Grade 8-B", "attendance": 87.5, "students": 32},
                {"class": "Grade 10-C", "attendance": 94.1, "students": 38},
            ],
        }

    def get_attendance_distribution(self):
        """
        Get distribution of students by attendance ranges.
        Only principals can access this.
        """
        # Mock data: attendance range distribution
        return {
            "success": True,
            "distribution": [
                {"range": "95-100%", "count": 156},
                {"range": "85-94%", "count": 512},
                {"range": "75-84%", "count": 385},
                {"range": "Below 75%", "count": 187},
            ],
        }

    def get_low_attendance_students(self, threshold=75):
        """
        Get students with attendance below threshold.
        Only principals can access this.
        """
        all_students = self.db.get_all_students()
        low_attendance = [
            {
                "student_id": s["student_id"],
                "name": s["name"],
                "attendance": s["attendance"],
                "class": s["class"],
            }
            for s in all_students
            if s["attendance"] < threshold
        ]

        return {
            "success": True,
            "threshold": threshold,
            "count": len(low_attendance),
            "students": low_attendance,
        }

    def format_attendance_message(self, stats):
        """
        Format school attendance statistics into a natural message.
        """
        return (
            f"The current overall school attendance is {stats['overall_attendance']:.1f}% "
            f"across {stats['total_students']} students with {stats['total_teachers']} teachers."
        )
