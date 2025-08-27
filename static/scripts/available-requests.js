document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll(".toggle-btn").forEach((button) => {
        button.addEventListener("click", function () {
            const card = this.closest(".request-card");
            const isSelected = card.getAttribute("data-selected") === "true";

            if (isSelected) {
                // Switch to OFF state
                card.setAttribute("data-selected", "false");
                card.classList.remove("selected");
                this.textContent = "Подать заявку";
            } else {
                // Switch to ON state
                card.setAttribute("data-selected", "true");
                card.classList.add("selected");
                this.textContent = "Отменить заявку";
            }
        });
    });
});
