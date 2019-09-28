"""This module handles the download of schedules from the online portal"""
from datetime import datetime
from requests import get


# TODO download exam dates too (probably unfeasible)
# TODO use datetime.date class instead of datetime.datetime
def download_from_portal(week_start: datetime) -> str:
    """downloads the schedule for a given week

    Args:
        week_start (datetime): first day of the week that has to be downloaded

    Raises:
        TypeError: argument is not a datetime object

    Returns:
        str: schedule. Is the content of an ics file.
    """
    if not isinstance(week_start, datetime):
        raise TypeError(f"{week_start} is not a datetime object")

    fmt = "%d-%m-%Y"
    formatted_week_start = week_start.strftime(fmt)

    # # I sem II e III anno
    # query_string = {
    #   'form-type': ['corso'],
    #   'list': ['0'],
    #   'faculty_group': ['0'],
    #   'anno': ['2018'],
    #   'scuola': ['Scuola_di_Scienze'],
    #   'corso': ['SC1167'],
    #   'anno2_multi': ['000ZZ|2', '000ZZ|3'],
    #   'anno2': ['000ZZ|2,000ZZ|3'],
    #   'date': [formatted_week_start],
    #   '_lang': ['it'],
    #   'ar_codes_': [
    #     'EC501492|EC501495|EC501496|EC470124|EC470125|EC470126|EC470128|EC470129'
    #   ],
    #   'ar_select_': ['true|false|true|true|true|true|true|false'],
    #   'txtaa': ['2018/2019'],
    #   'txtcorso': ['SC1167 - Informatica (Laurea)']
    # }

    # # II sem II e III anno
    # query_string = {
    #     "form-type": "corso",
    #     "list": "0",
    #     "faculty_group": "0",
    #     "anno": "2018",
    #     "scuola": "Scuola_di_Scienze",
    #     "corso": "SC1167",
    #     "anno2_multi": ["000ZZ|2", "000ZZ|3"],
    #     "anno2": ["000ZZ|2,000ZZ|3"],
    #     "date": formatted_week_start,
    #     "_lang": "it",
    #     "ar_codes_": "EC501491|EC501460|EC501493|EC470124|EC501494",
    #     "ar_select_": "true|false|true|true|true",
    #     "txtaa": "2018/2019",
    #     "txtcorso": "SC1167 - Informatica (Laurea)",
    # }

    # I sem I, II e III anno
    query_string = {
        "anno": "2019",
        "corso": "SC1167",
        "anno2": "000ZZ|1,000ZZ|2,000ZZ|3",
        "date": formatted_week_start,
        "ar_codes_": "EC546722|EC546719|EC530661|EC546726|EC501558|EC546720|EC546724|EC530664|EC501559|EC530665|EC501525|EC501556|EC501557",
        "ar_select_": "false|true|false|false|true|true|false|false|false|true|false|false|false",
    }

    url = "http://www.gestionedidattica.unipd.it/PortaleStudenti/ec_download_ical_grid.php"  # pylint: disable=line-too-long

    print("making request")
    req = get(url, params=query_string)

    return req.text


if __name__ == "__main__":
    RESPONSE = download_from_portal(datetime.now())
    print(RESPONSE)
