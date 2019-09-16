"""Contains classes for my specific implementation of an event"""

from datetime import datetime, date
import re

from icalendar import Event as VEvent
from pytz import timezone

from courses import MyCourses


class MyBaseEvent:
    """base event class"""

    def __init__(self, summary, location, description):
        self.summary: str = summary
        self.location: str = location
        self.description: str = description

    @classmethod
    def from_ical_event(cls, event):
        """Abstract method"""

    def to_gcal_event(self):
        """Abstract method"""


class MyEvent(MyBaseEvent):
    """A generic calendar event.

    Can be created from an ical event, and converted to a google event resource
    """

    pattern = re.compile(r" ([a-zA-Z0-9]+?) \[(.+?)\]")

    def __init__(self, summary, start_time, end_time, location, description):
        super().__init__(summary, location, description)

        if not isinstance(start_time, datetime):
            raise TypeError("start_time is not a datetime object")
        if not isinstance(end_time, datetime):
            raise TypeError("end_time is not a datetime object")

        if not start_time.tzinfo:
            start_time = timezone("Europe/Rome").localize(start_time)
        if not end_time.tzinfo:
            end_time = timezone("Europe/Rome").localize(end_time)

        self.start_time: datetime = start_time
        self.end_time: datetime = end_time

    def __repr__(self):
        return (
            f"{self.summary}, {self.start_time} - {self.end_time}"
            f" @ {self.location}; {self.description}."
        )

    @classmethod
    def from_ical_event(cls, event):
        """ parses an icalendar.Event object.

        !!! This code depends on the specific format of ics files produced by
        http://www.gestionedidattica.unipd.it/PortaleStudenti. it SHOULD also
        work for a generic ical event.
        """
        if not isinstance(event, VEvent):
            raise TypeError()

        summary = str(event["summary"])
        description = str(event["description"])

        if "location" in event:
            location = str(event["location"])
        else:
            description = description.replace(summary + " ", "").replace(" Lezione", "")
            it = cls.pattern.finditer(description)
            description = cls.pattern.sub("", description)

            if not it:
                raise ValueError("could not parse text: " + description)

            matches = []
            for el in it:
                matches.append(f"{el.group(1)} ({el.group(2)})")

            location = ", ".join(matches)

        start: datetime = event["dtstart"].dt

        # TODO: make some sick subclassing to distinguish all day events!
        if event["dtend"] is None and start.hour == 0 and start.minute == 0:
            # dayafter = start.day + 1
            start = start.replace(hour=8, minute=30)
            end = start.replace(hour=18)
            summary += "chiusura uni?"
        else:
            end = event["dtend"].dt

        return cls(summary, start, end, location, description)

    def to_gcal_event(self):
        event = {
            "kind": "calendar#event",
            "summary": self.summary,
            "description": self.description,
            "location": self.location,
            "start": {"dateTime": self.start_time.isoformat()},
            "end": {"dateTime": self.end_time.isoformat()},
        }

        try:
            event["colorId"] = MyCourses.get_course_color(self.summary)
        except ValueError as err:
            print(err)

        return event

    def event_id(self) -> str:
        """Calculates the id for this event """
        raw_id = "summary{}week{}start{}end{}".format(
            self.summary.lower(),
            self.start_time.isocalendar()[1],
            self.start_time.isoformat(),
            self.end_time.isoformat(),
        )

        valid_id = re.sub(r"[^a-z0-9]", "", raw_id)

        return valid_id


class MyAllDayEvent(MyBaseEvent):  # TODO finish this...
    """Represents an all day event

    Raises:
        NotImplementedError: is not implemented yet
    """

    def __init__(self, summary, start_date, end_date, location, description):
        super().__init__(self, summary, location, description)

        if not isinstance(start_date, date):
            raise TypeError("start_date is not a date object")
        if not isinstance(end_date, date):
            raise TypeError("end_date is not a date object")

        if not start_date.tzinfo:
            start_date = timezone("Europe/Rome").localize(start_date)
        if not end_date.tzinfo:
            end_date = timezone("Europe/Rome").localize(end_date)

        self.start_date = start_date
        self.end_date = end_date

        raise NotImplementedError

    def to_gcal_event(self):
        event = {
            "kind": "calendar#event",
            "summary": self.summary,
            "description": self.description,
            "location": self.location,
            "start": {"date": self.start_date.isoformat()},
            "end": {"date": self.end_date.isoformat()},
        }

        # TODO reduce code duplication

        try:
            event["colorId"] = MyCourses.get_course_color(self.summary)
        except ValueError as err:
            print(err)

        return event

    # def __eq__(self, other):
    #     return (
    #       self.start_time == other.start_time
    #       and self.end_time == other.end_time
    #       and self.summary == other.summary)

    # def __ne__(self, other):
    #     return not self == other

    # def __lt__(self, other):
    #     if self.start_time == other.start_time:
    #         return self.end_time < other.end_time
    #     return self.start_time < other.start_time

    # def __gt__(self, other):
    #     if self.start_time == other.start_time:
    #         return self.end_time > other.end_time
    #     return self.start_time > other.start_time
