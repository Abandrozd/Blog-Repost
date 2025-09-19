const today = new Date();
let currentYear = today.getFullYear();
let currentMonth = today.getMonth() + 1; // 1-based

const monthNames = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль",
    "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
];

function isActionDay(date) {
    return actionDates.includes(date);
}
function isRequestDay(date) {
    return requestDates.includes(date);
}

function renderCalendar(year, month) {
    const calendar = document.getElementById("calendar");
    calendar.innerHTML = '';
    let d = new Date(year, month - 1, 1);

    let table = document.createElement('table');
    let row = document.createElement('tr');

    // Header (days of week)
    ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].forEach(h => {
        let th = document.createElement('th');
        th.textContent = h;
        row.appendChild(th);
    });
    table.appendChild(row);
    row = document.createElement('tr');

    // Empty cells before first day
    let weekDay = d.getDay();
    weekDay = (weekDay + 6) % 7;
    for (let i = 0; i < weekDay; i++) {
        let empty = document.createElement('td');
        empty.className = "calendar-empty";
        row.appendChild(empty);
    }

    // Main calendar loop
    while (d.getMonth() === month - 1) {
        let cell = document.createElement('td');
        let yearNum = d.getFullYear();
        let monthNum = (d.getMonth() + 1).toString().padStart(2, '0');
        let dayNum = d.getDate().toString().padStart(2, '0');
        let dateStr = `${yearNum}-${monthNum}-${dayNum}`;

        cell.textContent = d.getDate();
        cell.className = "calendar-day";

        if (isActionDay(dateStr)) {
            cell.style.background = "#3adb62";
            cell.title = "В этот день вы должны сделать репост!";
            cell.onclick = function() { window.location.href = "/requests/"; };
            cell.style.cursor = "pointer";
        } else if (isRequestDay(dateStr)) {
            cell.style.background = "#2196F3";
            cell.title = "В этот день вы подали заявку";
            const reqId = ownRequestMap[dateStr];
            if (reqId) {
                cell.onclick = function() {
                    window.location.href = "/requests/" + reqId + "/details/";
                };
                cell.style.cursor = "pointer";
            }
        } else {
            cell.style.background = "#ffc0cb";
            cell.title = "Действий не требуется";
        }

        cell.addEventListener("mouseenter", function () {
            cell.classList.add("calendar-hover");
        });
        cell.addEventListener("mouseleave", function () {
            cell.classList.remove("calendar-hover");
        });

        if (((d.getDay() + 6) % 7) === 6) {
            row.appendChild(cell);
            table.appendChild(row);
            row = document.createElement('tr');
        } else {
            row.appendChild(cell);
        }
        d.setDate(d.getDate() + 1);
    }

    if (row.children.length) table.appendChild(row); // trailing days

    calendar.appendChild(table);
}

function updateCalendarHeader() {
    document.getElementById('calendar-title').textContent =
        monthNames[currentMonth - 1] + " " + currentYear;
}

function redrawCalendar() {
    renderCalendar(currentYear, currentMonth);
    updateCalendarHeader();
}

// --- On page load ---

document.addEventListener("DOMContentLoaded", function() {
    // Navigation
    document.getElementById('prev-month').onclick = function() {
        currentMonth--;
        if (currentMonth < 1) {
            currentMonth = 12;
            currentYear--;
        }
        redrawCalendar();
    };
    document.getElementById('next-month').onclick = function() {
        currentMonth++;
        if (currentMonth > 12) {
            currentMonth = 1;
            currentYear++;
        }
        redrawCalendar();
    };
    redrawCalendar(); // only this init needed!
});
