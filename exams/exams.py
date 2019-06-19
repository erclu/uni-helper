import typing
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from selenium import webdriver

instances = {
  .5: "I parziale",
  .99: "II parziale",
  1: "I",
  2: "II",
  3: "III",
  4: "IV",
  5: "V",
  6: "VI",
  7: "VII",
}


@dataclass
class Exam:
    course: str
    instance: typing.Union[int, float]
    start_time: datetime
    end_time: datetime
    location: str


chromedriver_path = Path(__file__
                         ).resolve().parent.joinpath("chromedriver74.exe")


def download_exams_list(date_from: date) -> str:

    def build_url(date_from: date) -> str:
        base_url = "https://gestionedidattica.unipd.it/PortaleStudenti/index.php"

        formatted_date_from = date_from.strftime("%d-%m-%Y")
        query_string_mapping = {
          'view': 'easytest',
          'form-type': 'et_cdl',
          'include': 'et_cdl',
          '_lang': 'it',
          'anno2': '1,2,3',
          'et_er': '1',
          'scuola': 'ScuoladiScienze',
          'esami_cdl': 'SC1167',
          'esami_cdl_anno': '1',
          'esami_cdl_anno': '2',
          'esami_cdl_anno': '3',
          'datefrom': formatted_date_from,
          'dateto': '30-09-2019',
          'list': '0',
          'week_grid_type': '-1',
          'col_cells': '0',
          'empty_box': '0',
          'only_grid': '0',
        }

        query_string = urlencode(query_string_mapping)

        return "{}?{}".format(base_url, query_string)

    url = build_url(date_from)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    driver = webdriver.Chrome(str(chromedriver_path), options=options)
    driver.implicitly_wait(15)

    driver.get(url)

    calendar_table: str = driver.find_element_by_css_selector(
      "div.calendar-table"
    ).get_attribute("outerHTML")

    driver.close()

    return calendar_table


def parse_response(html_response: str) -> typing.List[Exam]:
    soup = BeautifulSoup(html_response, 'html.parser')
    print(soup.prettify())

    rows = soup.select(".calendar-table-row")

    return None


def main() -> None:
    # html_response = download_exams_list(date.today())
    # Path("./response.html").write_text(html_response, encoding="utf-8")

    html_response = Path("./response.html").read_text()
    parse_response(html_response)


if __name__ == "__main__":
    main()
