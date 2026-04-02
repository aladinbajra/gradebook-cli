"""Business logic for the Gradebook application.

This module contains the rules for managing students, courses, enrollments,
and grades. It is designed to be callable from both the CLI and unit tests.
"""

import logging
from typing import Any

from .models import Course, Enrollment, Student
from .validators import parse_grade

logger = logging.getLogger(__name__)

_DATA: dict | None = None


def set_data(data: dict) -> None:
    """Set the in-memory gradebook data used by the service."""
    global _DATA
    _DATA = data


def _require_data() -> dict:
    if _DATA is None:
        raise RuntimeError("Service data not set. Call service.set_data(data).")
    return _DATA


def _next_id(records: list[dict]) -> int:
    if not records:
        return 1
    return max(r["id"] for r in records) + 1


def add_student(name: str) -> int:
    """Add a student and return the assigned ID.

    Args:
        name: Student full name.

    Returns:
        The assigned integer ID.

    Raises:
        ValueError: If the name is invalid.
    """
    data = _require_data()
    student_id = _next_id(data["students"])
    student = Student(student_id, name)
    data["students"].append({"id": student.id, "name": student.name})
    logger.info("Added student: %s", student)
    return student_id


def list_students(sort_by: str = "name") -> list[dict]:
    """List students sorted by name (default) or id.

    Args:
        sort_by: ``"name"`` or ``"id"`` (anything else falls back to ``"id"``).

    Returns:
        A sorted list of student dictionaries.
    """
    data = _require_data()
    key = "name" if sort_by == "name" else "id"
    return sorted(data["students"], key=lambda s: s[key])


def add_course(code: str, title: str) -> None:
    """Add a course.

    Args:
        code: Course code (case-insensitive; will be normalized).
        title: Course title.

    Raises:
        ValueError: If the course is invalid or already exists.
    """
    data = _require_data()
    course = Course(code, title)
    if any(c["code"] == course.code for c in data["courses"]):
        raise ValueError(f"Course '{course.code}' already exists.")
    data["courses"].append({"code": course.code, "title": course.title})
    logger.info("Added course: %s", course)


def list_courses(sort_by: str = "code") -> list[dict]:
    """List courses sorted by code (default) or title.

    Args:
        sort_by: ``"code"`` or ``"title"`` (anything else falls back to ``"code"``).

    Returns:
        A sorted list of course dictionaries.
    """
    data = _require_data()
    key = "title" if sort_by == "title" else "code"
    return sorted(data["courses"], key=lambda c: c[key])


def _get_student(student_id: int) -> dict:
    data = _require_data()
    matches = [s for s in data["students"] if s["id"] == student_id]
    if not matches:
        raise ValueError(f"No student found with ID {student_id}.")
    return matches[0]


def _get_course(course_code: str) -> dict:
    data = _require_data()
    code = course_code.strip().upper()
    matches = [c for c in data["courses"] if c["code"] == code]
    if not matches:
        raise ValueError(f"No course found with code '{course_code}'.")
    return matches[0]


def _get_enrollment(student_id: int, course_code: str) -> dict:
    data = _require_data()
    code = course_code.strip().upper()
    matches = [
        e
        for e in data["enrollments"]
        if e["student_id"] == student_id and e["course_code"] == code
    ]
    if not matches:
        raise ValueError(f"Student {student_id} is not enrolled in '{course_code}'.")
    return matches[0]


def enroll(student_id: int, course_code: str) -> None:
    """Enroll a student in a course.

    Args:
        student_id: Student ID.
        course_code: Course code.

    Raises:
        ValueError: If the student/course doesn't exist or enrollment already exists.
    """
    data = _require_data()
    _get_student(student_id)
    course = _get_course(course_code)
    if any(
        e["student_id"] == student_id and e["course_code"] == course["code"]
        for e in data["enrollments"]
    ):
        raise ValueError(f"Student {student_id} is already enrolled in '{course['code']}'.")
    enrollment = Enrollment(student_id, course["code"])
    data["enrollments"].append(
        {
            "student_id": enrollment.student_id,
            "course_code": enrollment.course_code,
            "grades": enrollment.grades,
        }
    )
    logger.info("Enrolled student %d in %s", student_id, course["code"])


def add_grade(student_id: int, course_code: str, grade: Any) -> None:
    """Add a grade for a student in a course.

    Args:
        student_id: Student ID.
        course_code: Course code.
        grade: Raw grade input (string or number).

    Raises:
        ValueError: If the student/course/enrollment is invalid or grade is invalid.
    """
    data = _require_data()
    _get_student(student_id)
    _get_course(course_code)
    enrollment_dict = _get_enrollment(student_id, course_code)
    validated = parse_grade(grade)
    enrollment = Enrollment(
        enrollment_dict["student_id"],
        enrollment_dict["course_code"],
        enrollment_dict.get("grades", []),
    )
    enrollment.add_grade(validated)
    enrollment_dict["grades"] = enrollment.grades
    logger.info("Added grade %.1f for student %d in %s", validated, student_id, course_code)


def list_enrollments() -> list[dict]:
    """List enrollments sorted by student_id."""
    data = _require_data()
    return sorted(data["enrollments"], key=lambda e: e["student_id"])


def compute_average(student_id: int, course_code: str) -> float:
    """Compute average grade for a student in a course.

    Args:
        student_id: Student ID.
        course_code: Course code.

    Returns:
        The numeric average as a float.
    """
    enrollment = _get_enrollment(student_id, course_code)
    grades = enrollment.get("grades", [])
    if not grades:
        raise ValueError(f"No grades recorded for student {student_id} in '{course_code}'.")
    return sum(grades) / len(grades)


def compute_gpa(student_id: int) -> float:
    """Compute student GPA as mean of course averages.

    Args:
        student_id: Student ID.

    Returns:
        GPA as a float.
    """
    data = _require_data()
    _get_student(student_id)
    enrollments = [
        e
        for e in data["enrollments"]
        if e["student_id"] == student_id and e.get("grades")
    ]
    if not enrollments:
        raise ValueError(f"Student {student_id} has no graded enrollments.")
    averages = [sum(e["grades"]) / len(e["grades"]) for e in enrollments]
    return sum(averages) / len(averages)