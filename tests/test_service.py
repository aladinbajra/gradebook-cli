"""Unit tests for the business logic in :mod:`gradebook.service`.

The goal of these tests is to validate both the happy paths and a handful of
edge cases (invalid names/grades, missing enrollments, and missing grades).
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gradebook.service import (
    set_data,
    add_student,
    add_course,
    enroll,
    add_grade,
    list_students,
    compute_average,
    compute_gpa,
)


def empty_data() -> dict:
    """Create a fresh empty gradebook data structure.

    Returns:
        A dict with empty ``students``, ``courses``, and ``enrollments`` lists.
    """
    return {"students": [], "courses": [], "enrollments": []}


class TestAddStudent(unittest.TestCase):
    """Tests for :func:`gradebook.service.add_student`."""

    def test_add_student_returns_id(self):
        """Adding a student should return an integer ID."""
        data = empty_data()
        set_data(data)
        student_id = add_student("Aladin Bajra")
        self.assertEqual(student_id, 1)
        self.assertEqual(len(data["students"]), 1)
        self.assertEqual(data["students"][0]["name"], "Aladin Bajra")

    def test_add_multiple_students_increments_id(self):
        """IDs should increment with each new student."""
        data = empty_data()
        set_data(data)
        id1 = add_student("Aladin Bajra")
        id2 = add_student("Altin Bajra")
        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)

    def test_add_student_empty_name_raises(self):
        """An empty/blank name should raise ``ValueError``."""
        data = empty_data()
        with self.assertRaises(ValueError):
            set_data(data)
            add_student("   ")


class TestAddGrade(unittest.TestCase):
    """Tests for :func:`gradebook.service.add_grade`."""

    def setUp(self):
        """Set up a student, course, and enrollment before each test.

        Returns:
            None
        """
        self.data = empty_data()
        set_data(self.data)
        add_student("Aladin Bajra")
        add_course("AA101", "AI Agentic Systems")
        enroll(1, "AA101")

    def test_add_grade_happy_path(self):
        """A valid grade should be appended to the enrollment's grades."""
        add_grade(1, "AA101", 95)
        enrollment = self.data["enrollments"][0]
        self.assertIn(95.0, enrollment["grades"])

    def test_add_multiple_grades(self):
        """Multiple grades can be added to the same enrollment."""
        add_grade(1, "AA101", 80)
        add_grade(1, "AA101", 90)
        enrollment = self.data["enrollments"][0]
        self.assertEqual(len(enrollment["grades"]), 2)

    def test_add_grade_above_100_raises(self):
        """A grade above 100 should raise ``ValueError``."""
        with self.assertRaises(ValueError):
            add_grade(1, "AA101", 105)

    def test_add_grade_below_0_raises(self):
        """A negative grade should raise ``ValueError``."""
        with self.assertRaises(ValueError):
            add_grade(1, "AA101", -5)

    def test_add_grade_unenrolled_raises(self):
        """Adding a grade for a course with no enrollment should fail."""
        add_course("ML102", "Machine Learning & NLP")
        with self.assertRaises(ValueError):
            add_grade(1, "ML102", 88)


class TestComputeAverage(unittest.TestCase):
    """Tests for :func:`gradebook.service.compute_average`."""

    def setUp(self):
        """Set up a student, course, and enrollment before each test.

        Returns:
            None
        """
        self.data = empty_data()
        set_data(self.data)
        add_student("Aladin Bajra")
        add_course("AA101", "AI Agentic Systems")
        enroll(1, "AA101")

    def test_compute_average_happy_path(self):
        """Average should be computed correctly from multiple grades."""
        add_grade(1, "AA101", 80)
        add_grade(1, "AA101", 100)
        avg = compute_average(1, "AA101")
        self.assertAlmostEqual(avg, 90.0)

    def test_compute_average_single_grade(self):
        """Average of a single grade should equal that grade."""
        add_grade(1, "AA101", 75)
        avg = compute_average(1, "AA101")
        self.assertAlmostEqual(avg, 75.0)

    def test_compute_average_no_grades_raises(self):
        """Computing an average with no grades should raise ``ValueError``."""
        with self.assertRaises(ValueError):
            compute_average(1, "AA101")


class TestComputeGPA(unittest.TestCase):
    """Tests for :func:`gradebook.service.compute_gpa`."""

    def test_compute_gpa_happy_path(self):
        """GPA should be the mean of course averages."""
        data = empty_data()
        set_data(data)
        add_student("Aladin Bajra")
        add_course("AA101", "AI Agentic Systems")
        add_course("ML102", "Machine Learning & NLP")
        enroll(1, "AA101")
        enroll(1, "ML102")
        add_grade(1, "AA101", 90)
        add_grade(1, "ML102", 80)
        gpa = compute_gpa(1)
        self.assertAlmostEqual(gpa, 85.0)

    def test_compute_gpa_no_grades_raises(self):
        """A student with no graded enrollments should raise ``ValueError``."""
        data = empty_data()
        set_data(data)
        add_student("Altin Bajra")
        with self.assertRaises(ValueError):
            compute_gpa(1)

    def test_compute_gpa_no_enrollments_raises(self):
        """A student with no enrollments should raise ``ValueError``."""
        data = empty_data()
        set_data(data)
        add_student("Olta Bajra")
        with self.assertRaises(ValueError):
            compute_gpa(1)

    def test_compute_gpa_enrolled_but_ungraded_raises(self):
        """A student enrolled in courses but with no grades should raise ``ValueError``."""
        data = empty_data()
        set_data(data)
        add_student("Aladin Bajra")
        add_course("AA101", "AI Agentic Systems")
        enroll(1, "AA101")
        with self.assertRaises(ValueError):
            compute_gpa(1)


class TestEdgeCases(unittest.TestCase):
    """Extra edge-case tests for the gradebook service."""

    def test_add_course_duplicate_raises(self):
        """Adding the same course code twice should fail."""
        data = empty_data()
        set_data(data)
        add_course("AA101", "AI Agentic Systems")
        with self.assertRaises(ValueError):
            add_course("AA101", "AI Agentic Systems v2")

    def test_enroll_duplicate_raises(self):
        """Enrolling twice in the same course should fail."""
        data = empty_data()
        set_data(data)
        add_student("Aladin Bajra")
        add_course("ML102", "Machine Learning & NLP")
        enroll(1, "ML102")
        with self.assertRaises(ValueError):
            enroll(1, "ML102")

    def test_add_grade_invalid_value_raises(self):
        """Non-numeric grade input should raise ``ValueError``."""
        data = empty_data()
        set_data(data)
        add_student("Aladin Bajra")
        add_course("AA101", "AI Agentic Systems")
        enroll(1, "AA101")
        with self.assertRaises(ValueError):
            add_grade(1, "AA101", "not-a-number")

    def test_compute_average_unenrolled_course_raises(self):
        """Computing average for a course with no enrollment should fail."""
        data = empty_data()
        set_data(data)
        add_student("Aladin Bajra")
        add_course("ML102", "Machine Learning & NLP")
        # No enroll() call here, so compute_average should fail.
        with self.assertRaises(ValueError):
            compute_average(1, "ML102")

    def test_list_students_sort_fallback_to_id(self):
        """Unknown sort key should fall back to sorting by ID."""
        data = empty_data()
        set_data(data)
        add_student("Zeta Bajra")
        add_student("Alpha Bajra")
        students = list_students(sort_by="does-not-exist")
        self.assertEqual([s["id"] for s in students], [1, 2])


if __name__ == "__main__":
    unittest.main()