"""Input validation helpers for the Gradebook CLI.

These helpers normalize common user inputs and raise ``ValueError`` with
messages that are safe to show in the terminal.
"""

from __future__ import annotations

from typing import Any


def parse_student_name(value: Any) -> str:
    """Validate and normalize a student name.

    Args:
        value: Raw input value (usually a string from the CLI).

    Returns:
        A trimmed, non-empty name string.

    Raises:
        ValueError: If the name is missing or only whitespace.
    """
    if value is None:
        raise ValueError("Student name is required.")
    name = str(value).strip()
    if not name:
        raise ValueError("Student name cannot be empty.")
    return name


def parse_course_code(value: Any) -> str:
    """Validate and normalize a course code.

    Args:
        value: Raw input value (usually a string from the CLI).

    Returns:
        A trimmed, uppercased course code.

    Raises:
        ValueError: If the course code is missing or empty.
    """
    if value is None:
        raise ValueError("Course code is required.")
    code = str(value).strip().upper()
    if not code:
        raise ValueError("Course code cannot be empty.")
    return code


def parse_grade(value: Any) -> float:
    """Parse and validate a numeric grade in ``[0, 100]``.

    Args:
        value: Raw grade value (string or number).

    Returns:
        Grade as a float.

    Raises:
        ValueError: If the grade is not numeric or outside the allowed range.
    """
    try:
        grade = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"'{value}' is not a valid number.")
    if not (0 <= grade <= 100):
        raise ValueError(f"Grade {grade} must be between 0 and 100.")
    return grade

