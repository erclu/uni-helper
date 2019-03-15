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


class MyCourses:
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
        return self._name

    @name.setter
    def name(self, name):
        lower = name.lower()
        if lower not in MyCourses._table["courses"]:
            raise ValueError(f"{lower} is not a valid course")
        self._name = lower

    @property
    def acronym(self):
        return self._acronym

    @property
    def color(self):
        return self._color

    @classmethod
    def get_course_color(cls, name):
        course = cls(name)
        return course.color
