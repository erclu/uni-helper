import argparse
from datetime import datetime as dt
from datetime import timedelta as td
from pathlib import Path

from icalendar import Calendar as VCalendar
from icalendar import Event as VEvent
from pytz import timezone as tz

from api_implementation import MyCalendarBatchInsert
from download_cal import download_from_portal
from my_event import MyEvent


def log(arg: str):
    print(arg)


def parse_ics_file(filename):
    """returns an icalendar.Calendar object given the ics filename"""
    with open(filename, "r", encoding="utf-8") as file:
        return VCalendar.from_ical(file.read())


def parse_ical(cal, weeks_to_filter):
    """builds a my_event.MyEvent object.

    args:
        cal -- an icalendar.Calendar object
        weeks_to_filter -- self explanatory
    """
    # if "prodid" not in cal:
    #     cal.add("prodid", "-//ErcLu//UniPD class schedule//IT")

    vevents = cal.walk("vevent")
    my_events = [MyEvent.from_ical_event(vevent) for vevent in vevents]

    if weeks_to_filter != -1:

        today = dt.now(tz("Europe/Rome")).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        next_sat = today + td((5 - today.weekday()) % 7)
        last_dt = next_sat + td(7 * weeks_to_filter)

        my_events = [x for x in my_events if x.start_time < last_dt]

    return my_events


def upload_to_google_calendar(events):
    """uploads a list of 5 my_event.MyEvent objects to google calendar.

    Returns the api response
    """
    batch = MyCalendarBatchInsert()

    for event in events:
        batch.add(event.to_gcal_event())

    return batch.execute()


def make_test_content():
    cal = VCalendar()
    # cal.add("VERSION", "2.0")
    cal.add("prodid", "-//ErcLu//test ical file//IT")

    now = dt.now()
    today = (now.year, now.month, now.day)

    for x in range(1, 6):
        event = VEvent()
        event.add("summary", f"test event #{x}")
        event.add("dtstart", dt(*today, 10 + 2 * x))
        event.add("dtend", dt(*today, 11 + 2 * x))
        # event.add("location", f"location #{x}")
        # event.add("description", f"description #{x}")
        event.add(
            "description",
            f"test event #{x} COGNOME1 NOME1, COGNOME2 NOME2 aula [posto dell'aula]"
        )

        cal.add_component(event)

    return cal


def parse_arguments(argv):
    parser = argparse.ArgumentParser(
        description="parses and uploads ics files to google calendar via API"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("filename", help="file to parse, minimum 1!", nargs="?")

    group.add_argument(
        "-t",
        "--make-test-ics",
        dest="test",
        action="store_true",
        help="creates 5 events on today's calendar",
    )

    group.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="downloads next weeks lessons from the webpage",
    )

    parser.add_argument(
        "--when",
        help="specify day in week to download schedule for (YY-MM-DD)",
        type=str,
        default="",
    )

    parser.add_argument(
        "-r",
        "--remove-files",
        dest="remove",
        help="remove parsed files",
        action="store_true",
    )

    parser.add_argument(
        "-u",
        "--upload",
        help="upload the events to google calendar",
        action="store_true",
    )

    parser.add_argument("-v", "--verbose", help="verbosity level", action="store_true")

    parser.add_argument(
        "-c",
        "--colors",
        help="update colors from class schedule gsheet",
        action="store_true",
    )

    group.add_argument(
        "--weeks",
        dest="weeks_to_filter",
        type=int,
        default=-1,
        help="filter to events within the next x weeks, where 0 means current"
        " week ! DOES NOTHING WHEN USED WITH --download",
    )

    args = parser.parse_args(argv)
    return args
    # return (
    #   args.file, args.download, args.remove, args.test, args.upload,
    #   args.verbose, args.weeks_to_filter)


def main(argv):
    parsed_args = parse_arguments(argv)
    log("parsed args")

    if parsed_args.test:
        content = make_test_content()

    elif parsed_args.filename:
        if not Path(parsed_args.filename).exists():
            raise ValueError(f"{parsed_args.filename} does not exist")

        print(f"parsing {parsed_args.filename}")
        content = parse_ics_file(parsed_args.filename)

    elif parsed_args.download:
        if not parsed_args.when:
            today = dt.now(tz("Europe/Rome")).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            next_mon = today + td((0 - today.weekday()) % 7)

            raw_content = download_from_portal(next_mon)
        else:
            when = dt.strptime(parsed_args.when, "%y-%m-%d")

            raw_content = download_from_portal(when)

        content = VCalendar.from_ical(raw_content)

    events = parse_ical(content, parsed_args.weeks_to_filter)

    print(f"found {len(events)} events")

    if parsed_args.colors:
        from api_implementation import update_courses_colors

        update_courses_colors()

    if parsed_args.verbose:
        for event in events:
            print(event)

    # for event in events:
    #     print(event.to_gcal_event())

    if parsed_args.upload:
        print(f"uploading...")
        upload_to_google_calendar(events)
        print(" Done.")

    if parsed_args.remove:
        Path(parsed_args.filename).unlink()
        print(f"removed {parsed_args.filename}")


if __name__ == "__main__":
    from sys import argv as sys_argv

    log("entering main")
    main(sys_argv[1:])
