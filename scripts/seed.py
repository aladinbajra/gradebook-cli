"""Seed script for the gradebook CLI.

It creates a small set of students, courses, enrollments, and grades and then
stores them in ``data/gradebook.json``.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gradebook.storage import save_data
from gradebook.service import (
    set_data,
    add_student,
    add_course,
    enroll,
    add_grade,
)


def seed():
    """Populate the JSON storage with sample gradebook data.

    The sample dataset is meant to make it easy to test the CLI commands
    quickly.

    Returns:
        None
    """
    data = {"students": [], "courses": [], "enrollments": []}

    set_data(data)

    id1 = add_student("Aladin Bajra")
    id2 = add_student("Altin Bajra")
    id3 = add_student("Olta Bajra")

    add_course("AA101", "AI Agentic Systems")
    add_course("ML102", "Machine Learning & NLP")

    enroll(id1, "AA101")
    enroll(id1, "ML102")
    enroll(id2, "AA101")
    enroll(id3, "ML102")

    add_grade(id1, "AA101", 92)
    add_grade(id1, "AA101", 88)
    add_grade(id1, "ML102", 75)
    add_grade(id1, "ML102", 81)

    add_grade(id2, "AA101", 70)
    add_grade(id2, "AA101", 65)

    add_grade(id3, "ML102", 95)
    add_grade(id3, "ML102", 100)

    save_data(data)
    print("  Seed complete! Data saved to data/gradebook.json")
    print(f"  Students   : {len(data['students'])}")
    print(f"  Courses    : {len(data['courses'])}")
    print(f"  Enrollments: {len(data['enrollments'])}")


if __name__ == "__main__":
    seed()