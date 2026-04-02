"""Gradebook CLI entry point.

This module handles argument parsing and user-facing output. Business rules
live in ``gradebook.service`` and persistence lives in ``gradebook.storage``.
"""

import argparse
import logging
import os

from gradebook.storage import load_data, save_data
from gradebook import service
from gradebook.validators import parse_course_code, parse_student_name, parse_grade


os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
    ]
)

logger = logging.getLogger(__name__)


def _print_table(headers: list[str], rows: list[list[str]]) -> None:
    """Print a simple aligned table to stdout.

    Args:
        headers: Column headers.
        rows: Table rows as strings.
    """
    if not rows:
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    header_line = "  " + "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    sep_line = "  " + "  ".join("-" * widths[i] for i in range(len(headers)))
    print(header_line)
    print(sep_line)
    for row in rows:
        print("  " + "  ".join(row[i].ljust(widths[i]) for i in range(len(headers))))


def handle_add_student(args, data):
    """Handle the ``add-student`` subcommand.

    Args:
        args: Parsed CLI args.
        data: Current in-memory gradebook dict.

    Returns:
        The (possibly updated) gradebook dict.
    """
    try:
        name = parse_student_name(args.name)
        student_id = service.add_student(name)
        save_data(data)
        print(f"  Student '{name}' added with ID {student_id}.")
    except ValueError as e:
        logger.error("add-student failed: %s", e)
        print(f"  Error: {e}")
    return data


def handle_add_course(args, data):
    """Handle the ``add-course`` subcommand.

    Args:
        args: Parsed CLI args.
        data: Current in-memory gradebook dict.

    Returns:
        The (possibly updated) gradebook dict.
    """
    try:
        code = parse_course_code(args.code)
        title = str(args.title).strip()
        if not title:
            raise ValueError("Course title cannot be empty.")
        service.add_course(code, title)
        save_data(data)
        print(f"  Course '{code} - {title}' added.")
    except ValueError as e:
        logger.error("add-course failed: %s", e)
        print(f"  Error: {e}")
    return data


def handle_enroll(args, data):
    """Handle the ``enroll`` subcommand."""
    try:
        course = parse_course_code(args.course)
        service.enroll(args.student_id, course)
        save_data(data)
        print(f"  Student {args.student_id} enrolled in '{course}'.")
    except ValueError as e:
        logger.error("enroll failed: %s", e)
        print(f"  Error: {e}")
    return data


def handle_add_grade(args, data):
    """Handle the ``add-grade`` subcommand."""
    try:
        course = parse_course_code(args.course)
        grade = parse_grade(args.grade)
        service.add_grade(args.student_id, course, grade)
        save_data(data)
        print(
            f"  Grade {grade} added for student {args.student_id} "
            f"in '{course}'."
        )
    except ValueError as e:
        logger.error("add-grade failed: %s", e)
        print(f"  Error: {e}")
    return data


def handle_list(args, data):
    """Handle the ``list`` subcommand."""
    sort = getattr(args, "sort", None)

    if args.target == "students":
        students = service.list_students(sort_by="name" if not sort or sort == "name" else "id")
        if not students:
            print("  No students found.")
            return data
        rows = [[str(s["id"]), str(s["name"])] for s in students]
        _print_table(["ID", "Name"], rows)

    elif args.target == "courses":
        courses = service.list_courses(sort_by="code" if not sort or sort == "code" else "title")
        if not courses:
            print("  No courses found.")
            return data
        rows = [[str(c["code"]), str(c["title"])] for c in courses]
        _print_table(["Code", "Title"], rows)

    elif args.target == "enrollments":
        enrollments = service.list_enrollments()
        if not enrollments:
            print("  No enrollments found.")
            return data
        rows = [
            [str(e["student_id"]), str(e["course_code"]), str(e.get("grades", []))]
            for e in enrollments
        ]
        _print_table(["Student ID", "Course", "Grades"], rows)
    return data


def handle_avg(args, data):
    """Handle the ``avg`` subcommand."""
    try:
        course = parse_course_code(args.course)
        avg = service.compute_average(args.student_id, course)
        print(
            f"  Average for student {args.student_id} "
            f"in '{course}': {avg:.2f}"
        )
    except ValueError as e:
        logger.error("avg failed: %s", e)
        print(f"  Error: {e}")
    return data


def handle_gpa(args, data):
    """Handle the ``gpa`` subcommand."""
    try:
        gpa = service.compute_gpa(args.student_id)
        print(f"  GPA for student {args.student_id}: {gpa:.2f}")
    except ValueError as e:
        logger.error("gpa failed: %s", e)
        print(f"  Error: {e}")
    return data


def build_parser() -> argparse.ArgumentParser:
    """Create the argparse parser.

    Returns:
        A configured ``ArgumentParser`` with all supported subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="gradebook",
        description="A simple CLI gradebook application."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_as = sub.add_parser("add-student", help="Add a new student.")
    p_as.add_argument("--name", required=True, help="Student full name.")

    p_ac = sub.add_parser("add-course", help="Add a new course.")
    p_ac.add_argument("--code", required=True, help="Course code (e.g. CS101).")
    p_ac.add_argument("--title", required=True, help="Course title.")

    p_en = sub.add_parser("enroll", help="Enroll a student in a course.")
    p_en.add_argument("--student-id", required=True, type=int, dest="student_id")
    p_en.add_argument("--course", required=True, help="Course code.")

    p_ag = sub.add_parser("add-grade", help="Add a grade for a student.")
    p_ag.add_argument("--student-id", required=True, type=int, dest="student_id")
    p_ag.add_argument("--course", required=True, help="Course code.")
    p_ag.add_argument("--grade", required=True, type=float, help="Grade (0-100).")

    p_li = sub.add_parser("list", help="List students, courses, or enrollments.")
    p_li.add_argument(
        "target",
        choices=["students", "courses", "enrollments"],
        help="What to list."
    )
    p_li.add_argument(
        "--sort",
        choices=["name", "code"],
        default=None,
        help="Sort by name or code."
    )

    p_av = sub.add_parser("avg", help="Compute average grade.")
    p_av.add_argument("--student-id", required=True, type=int, dest="student_id")
    p_av.add_argument("--course", required=True, help="Course code.")

    p_gp = sub.add_parser("gpa", help="Compute student GPA.")
    p_gp.add_argument("--student-id", required=True, type=int, dest="student_id")

    return parser


HANDLERS = {
    "add-student": handle_add_student,
    "add-course":  handle_add_course,
    "enroll":      handle_enroll,
    "add-grade":   handle_add_grade,
    "list":        handle_list,
    "avg":         handle_avg,
    "gpa":         handle_gpa,
}


def main():
    """Run the CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()
    data = load_data()
    service.set_data(data)
    data = HANDLERS[args.command](args, data)


if __name__ == "__main__":
    main()