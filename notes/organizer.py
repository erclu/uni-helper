"""parses and organizes the notes files i took with styluslabs write"""
import typing
from datetime import datetime
from pathlib import Path

from lxml import etree
from reportlab.graphics import renderPDF
from reportlab.pdfgen.canvas import Canvas
from svglib.svglib import SvgRenderer as svg_renderer

NOTES_PATH: Path = Path("D:/Users/erclu/Google Drive/UploadedNotes")
COURSES_FOLDER: Path = Path("D:/Users/erclu/Documents/Università")


# TODO manage missing classes
class Bookmark:
    """represents a bookmark in a page.

    attr
        position: relative to the page
        dtime: datetime of when the bookmark was taken
    """

    def __init__(self, position, dtime):
        self.position: int = position
        self.dtime: datetime = dtime

    def __repr__(self):
        return "Bookmark(pos: {}, dtime: {})".format(self.position, self.dtime)

    @classmethod
    def from_node(cls, node, height):
        """builds the bookmark given a node and its position"""
        position = int(Page.scale * (15.0 + float(height) - float(node.get("__comy"))))
        # position = int(float(node.get("__comy")))*Page.scale
        dtime = datetime.fromtimestamp(int(node.get("__timestamp"), 0) / 1000)

        return cls(position, dtime)


class Page:
    """represents an svg file containing part of the notes i've written"""

    scale = 72 / 150

    def __init__(self, path: Path):
        if not path.exists():
            raise IOError("svg page does not exist")

        self._path: Path = path

        timestamp = int(round(self._path.stat().st_mtime))
        self.last_modified = datetime.fromtimestamp(timestamp)

        # lazy initialization
        self._bookmarks, self._drawing = None, None

        # self.load()

    @property
    def bookmarks(self) -> typing.List[Bookmark]:
        """List of bookmarks on this page"""
        if self._bookmarks is None:
            self.load()

        return self._bookmarks

    @property
    def drawing(self):
        """Returns a rendered Reportlab Drawing instance"""
        if self._drawing is None:
            self.load()

        return self._drawing

    def load(self) -> None:
        """performs intensive loading operations lazily"""

        print(f"loading {self._path.name}...", end="")

        parser = etree.XMLParser(remove_comments=True, recover=True)
        tree = etree.parse(str(self._path), parser=parser)

        def load_bookmarks() -> typing.List[str]:
            xmlns = "{" + "http://www.w3.org/2000/svg" + "}"
            nodes = tree.iterfind(f"/{xmlns}g/{xmlns}path[@class='bookmark']")
            page_height = tree.find(f"/{xmlns}g").get("height")
            return [Bookmark.from_node(node, page_height) for node in nodes]

        def load_svg():
            drawing = svg_renderer(self._path).render(tree.getroot())

            drawing.width = drawing.minWidth() * Page.scale
            drawing.height *= Page.scale
            drawing.scale(Page.scale, Page.scale)
            return drawing

        self._bookmarks = load_bookmarks()
        self._drawing = load_svg()
        print(" Done")


# FIXME SO MANY SIDE EFFECTS I CAN'T EVEN
def generate_folder_names(courses, folder: Path):
    """ugly way to generate the course folders"""
    for course_name in courses:
        found = next(folder.glob("*{}*".format(course_name)), None)
        if found:
            courses[course_name]["folder"] = found


class Course:  # TODO refactor to external package
    """represents one of the courses i'm attending"""

    root_folder: Path = COURSES_FOLDER

    courses_attended = {
        "architettura degli elaboratori": {"acronym": "AdE"},
        "logica": {"acronym": "L"},
        "reti e sicurezza": {"acronym": "ReS"},
        "algoritmi e strutture dati": {"acronym": "AeSD"},
        "calcolo numerico": {"acronym": "CN"},
        "probabilita' e statistica": {"acronym": "PeS"},
        "ingegneria del software": {"acronym": "IdS"},
    }

    old_courses_attended = {
        "reti e sicurezza": {
            "acronym": "ReS",
            "folder": root_folder.joinpath("_21.Reti e sicurezza"),
        },
        "ingegneria del software": {
            "acronym": "IdS",
            "folder": root_folder.joinpath("_31-2.Ingegneria del software"),
        },
        "ricerca operativa": {
            "acronym": "RO",
            "folder": root_folder.joinpath("_31.Ricerca operativa"),
        },
        "tecnologie web": {
            "acronym": "TW",
            "folder": root_folder.joinpath("_31.Tecnologie web"),
        },
        "probabilita' e statistica": {"acronym": "PeS", "folder": ""},
    }

    def __init__(self, name: str):

        if name.lower() not in Course.courses_attended:
            found = False

            # search if name is an acronym...
            for course_name, attr in Course.courses_attended.items():
                if name == attr["acronym"]:
                    found = course_name
                    break

            if found:
                name = found.capitalize()
            else:
                raise ValueError("not a valid course: {}".format(name))

        self.name: str = name

    @property
    def acronym(self) -> str:
        """acronym for this course"""
        return self.courses_attended[self.name.lower()]["acronym"]

    @property
    def folder(self) -> Path:
        """folder path for this course"""
        matching_folder: typing.List[Path] = [
            x for x in self.root_folder.glob("*{}*".format(self.name.lower()))
        ]
        if len(matching_folder) != 1:
            raise ValueError("something wrong with the course folder")

        return matching_folder[0]

    # def get_all_pdfs(self) -> typing.List[CoursePdf]:
    #     notes_pdfs: typing.List[CoursePdf] = [
    #       CoursePdf.from_instance(x)
    #       for x in self.folder.glob("*Appunti*.pdf")
    #     ]
    #     print(
    #       "found {} pdfs for course {}!".format(len(notes_pdfs), self.name))


def notes_name_schema(arg) -> str:
    """this is the naming template for notes files"""
    return "_Appunti {}.pdf".format(arg)


class CoursePdf:
    """represents an instance of the pdf containing the notes for a course.

    title: name of the file
    course:
    path: file path
    """

    def __init__(self, init_arg):

        self.title = init_arg
        self.course = Course(init_arg.split(" - ")[0])

        self.path: Path = Path(self.course.folder, notes_name_schema(self.title))

    def exists(self) -> bool:
        """checks if the pdf exists"""
        return self.path.exists()

    def last_modified(self) -> datetime:
        """checks when the file was last modified"""
        if not self.exists():
            return datetime.min
        timestamp = int(round(self.path.stat().st_mtime))
        return datetime.fromtimestamp(timestamp)

    # @classmethod
    # def from_instance(cls, path: Path):
    #     name = path.name.replace("Appunti ", "").replace(".pdf", "")

    #     return cls(name)


class CourseNotes:
    """builds a course notes object from the path of the html wrapper file"""

    def __init__(self, name: str, pages: typing.List[Page]):
        self.pdf: CoursePdf = CoursePdf(name)
        self.pages: typing.List[Page] = pages

    def last_modified_page(self) -> datetime:
        """Return the most recently modified page"""
        most_recent_page = max(self.pages, key=lambda x: x.last_modified)

        return most_recent_page.last_modified

    def update_pdf(self) -> None:
        """Checks whether the notes pdf is up to date"""
        if self.last_modified_page() > self.pdf.last_modified():
            print("need to remake {}".format(self.pdf.title))
            self.create_pdf()
        else:
            print("{} is up to date...".format(self.pdf.title))

    def create_pdf(self) -> None:
        """Creates this course notes pdf file"""
        print(f"making {self.pdf.title}")
        if self.pdf.exists():
            self.pdf.path.unlink()

        canvas = Canvas(str(self.pdf.path))
        canvas.setAuthor("Luca Ercole")

        for page in self.pages:
            drawing = page.drawing
            canvas.setPageSize((drawing.width, drawing.height))

            renderPDF.draw(drawing, canvas, 0, 0)

            for bookmark in page.bookmarks:
                exact_ts = bookmark.dtime
                title = exact_ts.replace(minute=30).isoformat()[:16]
                pos = bookmark.position

                canvas.bookmarkPage(key=str(exact_ts), fit="XYZ", top=pos)
                # canvas.addOutlineEntry(title=title, key=title)
                canvas.addOutlineEntry(title=title, key=str(exact_ts))
                # canvas.drawString(0, pos, str(pos))

            canvas.showPage()

        canvas.save()
        print("Done")

    @classmethod
    def from_note_html(cls, path: Path):
        """builds a course notes object from the path of the html wrapper file"""
        parser = etree.XMLParser(ns_clean=True, remove_comments=True)
        tree = etree.parse(str(path), parser)

        xmlns = "{" + tree.getroot().nsmap.get(None) + "}"

        title_node = tree.find(
            f"/{xmlns}head/{xmlns}script/{xmlns}string[@name='docTitle']"
        )

        assert title_node is not None

        title = title_node.get("value")

        it = tree.iterfind(f"/{xmlns}body/{xmlns}object")

        pages_paths: typing.List[Path] = [
            Path(NOTES_PATH / obj.get("data")) for obj in it
        ]
        print(f"filename: {path.name}, title: {title}, {len(pages_paths)} pages")

        assert pages_paths and all(p.exists() for p in pages_paths), (
            "pages found while parsing html: " + pages_paths
        )

        pages = [Page(x) for x in pages_paths]

        try:
            result = cls(title, pages)
            return result
        except ValueError as err:
            raise ValueError("error on file {}".format(path)) from err


def main():  # pylint: disable=missing-docstring
    gen = NOTES_PATH.glob("*html")
    courses: typing.List[CourseNotes] = [CourseNotes.from_note_html(p) for p in gen]

    for course in courses:
        course.update_pdf()


if __name__ == "__main__":
    main()
