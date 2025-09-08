function isActionDay(date) {
    return actionDates.includes(date);
}

function renderCalendar(year, month) {
    const calendar = document.getElementById("calendar");
    calendar.innerHTML = '';
    let d = new Date(year, month - 1, 1);
    let table = document.createElement('table');
    let row = document.createElement('tr');

    // Weekday headers
    ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].forEach(h => {
        let th = document.createElement('th');
        th.textContent = h;
        row.appendChild(th);
    });
    table.appendChild(row);
    row = document.createElement('tr');

    // Padding at start for correct weekday
    let weekDay = d.getDay();
    weekDay = (weekDay + 6) % 7; // Mon=0, Sun=6
    for (let i = 0; i < weekDay; i++) {
        let empty = document.createElement('td');
        empty.className = "calendar-empty";
        row.appendChild(empty);
    }

    // Fill days
    while (d.getMonth() === month - 1) {
        let cell = document.createElement('td');
        let yearNum = d.getFullYear();
        let monthNum = (d.getMonth() + 1).toString().padStart(2, '0');
        let dayNum = d.getDate().toString().padStart(2, '0');
        let dateStr = `${yearNum}-${monthNum}-${dayNum}`;

        cell.textContent = d.getDate();
        cell.className = "calendar-day";
        if (isActionDay(dateStr)) {
            cell.style.background = "#3ad3ff";
            cell.title = "В этот день ожидается ваш репост!";
        } else {
            cell.style.background = "#ffc0cb";
            cell.title = "Действий не требуется";
        }

        // Add modern hover with a class (rest is handled by your CSS)
        cell.addEventListener("mouseenter", function () {
            cell.classList.add("calendar-hover");
        });
        cell.addEventListener("mouseleave", function () {
            cell.classList.remove("calendar-hover");
        });

        // End of week: close row
        if (((d.getDay() + 6) % 7) === 6) {
            row.appendChild(cell);
            table.appendChild(row);
            row = document.createElement('tr');
        } else {
            row.appendChild(cell);
        }
        d.setDate(d.getDate() + 1);
    }

    // If leftovers, pad row at end
    if (row.children.length) table.appendChild(row);

    calendar.appendChild(table);
}

const today = new Date();
renderCalendar(today.getFullYear(), today.getMonth() + 1);
