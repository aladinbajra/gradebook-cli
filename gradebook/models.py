"""Core data models for the Gradebook application.

These classes are small value objects used by the business logic for validation
and readable string representations.
"""


class Student:
    """A student with an ID and a name.

    Attributes:
        id: Auto-assigned numeric identifier.
        name: Student full name.
    """

    def __init__(self, student_id: int, name: str):
        """Create a :class:`Student`.

        Args:
            student_id: Assigned identifier for the student.
            name: Student full name.

        Raises:
            ValueError: If ``name`` is empty or only whitespace.

        Returns:
            None
        """
        if not name.strip():
            raise ValueError("Student name cannot be empty.")
        self.id = student_id
        self.name = name.strip()

    def __str__(self):
        """Return a readable representation.

        Returns:
            A string in the form ``[id] name``.
        """
        return f"[{self.id}] {self.name}"


class Course:
    """A course with a code and title.

    Attributes:
        code: Normalized course code (uppercased).
        title: Course title.
    """

    def __init__(self, code: str, title: str):
        """Create a :class:`Course`.

        Args:
            code: Course code (for example, ``CS101``).
            title: Course title.

        Raises:
            ValueError: If ``code`` or ``title`` are empty.

        Returns:
            None
        """
        if not code.strip():
            raise ValueError("Course code cannot be empty.")
        if not title.strip():
            raise ValueError("Course title cannot be empty.")
        self.code = code.strip().upper()
        self.title = title.strip()

    def __str__(self):
        """Return a readable representation.

        Returns:
            A string in the form ``[code] title``.
        """
        return f"[{self.code}] {self.title}"


class Enrollment:
    """A student's enrollment in a course.

    Attributes:
        student_id: ID of the student.
        course_code: Normalized course code (uppercased).
        grades: List of validated numeric grades.
    """

    def __init__(self, student_id: int, course_code: str, grades: list = None):
        """Create an :class:`Enrollment`.

        Args:
            student_id: ID of the student being enrolled.
            course_code: Course code (will be normalized to uppercase).
            grades: Optional list of initial grades. Each grade is validated.

        Returns:
            None
        """
        self.student_id = student_id
        self.course_code = course_code.strip().upper()
        self.grades = []
        if grades:
            for g in grades:
                self.add_grade(g)

    def add_grade(self, grade: float):
        """Add a validated grade to this enrollment.

        Args:
            grade: Numeric grade that must fall within ``[0, 100]``.

        Raises:
            ValueError: If the grade is outside ``0`` to ``100``.

        Returns:
            None
        """
        if not (0 <= grade <= 100):
            raise ValueError(f"Grade {grade} is invalid. Must be between 0 and 100.")
        self.grades.append(grade)

    def __str__(self):
        """Return a readable representation.

        Returns:
            A string summarizing the enrollment and its grades.
        """
        return (f"Student {self.student_id} | "
                f"Course {self.course_code} | "
                f"Grades: {self.grades}")