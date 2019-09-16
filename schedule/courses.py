"""This module contains stuff relative to the course object for this package"""

import json
from pathlib import Path

COLORS = {
    "PALE_BLUE": "1",
    "PALE_GREEN": "2",
    "MAUVE": "3",
    "PALE_RED": "4",
    "YELLOW": "5",
    "ORANGE": "6",
    "CYAN": "7",
    "GRAY": "8",
    "BLUE": "9",
    "GREEN": "10",
    "RED": "11",
}

VALID_COURSES: Path = Path(__file__).resolve().parents[1].joinpath(
    "resources", "courses_table.json"
)


def get_table_content():
    """gets the content of local file with the courses table"""
    content = VALID_COURSES.read_text()
    return json.loads(content)


class MyCourses:  # TODO refactor to external package
    """represents a course. Has a table of valid courses, loaded from a file."""

    _table = None

    def __init__(self, name):
        if MyCourses._table is None:
            print(f"opening {VALID_COURSES}...", end="")
            MyCourses._table = get_table_content()
            print(" Done.")
        self._name = None

        self.name = name
        properties = MyCourses._table["courses"][self.name]
        self._acronym = properties["acronym"]
        self._color = COLORS[properties["color"]]

    def __repr__(self):
        return f"{self.name} ({self.acronym}, {self.color})"

    @property
    def name(self):
        """course name

        Raises:
            ValueError: when attempting to create a non existing course

        Returns:
            str: name of the course
        """
        return self._name

    @name.setter
    def name(self, name: str) -> str:
        lower = name.lower()
        if lower not in MyCourses._table["courses"]:
            raise ValueError(f"{lower} is not a valid course")
        self._name = lower

    @property
    def acronym(self) -> str:
        """course acronym

        Returns:
            str: acronym of the course
        """
        return self._acronym

    @property
    def color(self) -> str:
        """color of this course in google calendar

        Returns:
            str: Name of the color
        """
        return self._color

    @classmethod
    def get_course_color(cls, name: str) -> str:
        """utility method to get course color without needing a Course instance

        Args:
            name (str): name of the course to check the color for

        Returns:
            str: the color of given course
        """
        course = cls(name)
        return course.color
