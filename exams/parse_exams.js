function run() {
  let rows = document.querySelectorAll(".calendar-table-row");
  let out = {
    exams: []
  };

  function parseRow(row) {
    let dateStr = row.querySelector(".er-calendar-table-col-data-test").innerText;
    let timesStr = row.querySelector(".er-calendar-table-col-ora-test").innerText.split(" - ");

    let courseStr = row.querySelector(".er-calendar-table-col-nome-test").innerText;
    let locationStr = row.querySelector(".er-calendar-table-col-aula-test").innerText;

    out.exams.push({
      date: dateStr,
      startTime: timesStr[0],
      endTime: timesStr[1],
      course: courseStr,
      location: locationStr
    });
  }

  rows.forEach(parseRow);
  console.log(JSON.stringify(out));
}

run();
// TODO convert to python!!!!
