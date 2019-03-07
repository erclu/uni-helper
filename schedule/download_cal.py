from datetime import datetime as dt
from requests import get

# pylint: disable=C0301


# TODO use datetime.date class instead of datetime.datetime
def download_from_portal(week_start):
    if not isinstance(week_start, dt):
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

    # II sem II e III anno
    query_string = {
      'form-type': ['corso'], # XXX why lists?
      'list': ['0'],
      'faculty_group': ['0'],
      'anno': ['2018'],
      'scuola': ['Scuola_di_Scienze'],
      'corso': ['SC1167'],
      'anno2_multi': ['000ZZ|2', '000ZZ|3'],
      'anno2': ['000ZZ|2,000ZZ|3'],
      'date': [formatted_week_start],
      '_lang': ['it'],
      'ar_codes_': ['EC501491|EC501460|EC501493|EC470124|EC501494'],
      'ar_select_': ['true|false|true|true|true'],
      'txtaa': ['2018/2019'],
      'txtcorso': ['SC1167 - Informatica (Laurea)'],
    }

    url = "http://www.gestionedidattica.unipd.it/PortaleStudenti/ec_download_ical_grid.php"

    print("making request")
    req = get(url, params=query_string)

    return req.text


if __name__ == '__main__':
    RESPONSE = download_from_portal(dt.now())
    print(RESPONSE)
