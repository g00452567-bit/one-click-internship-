
function exploreInternships() {
    document.getElementById("internships").scrollIntoView({
        behavior: "smooth"
    });
}

function searchInternships() {
    const input = document.getElementById("searchInput");
    const value = input.value.trim().toLowerCase();

    const cards = document.querySelectorAll(".internship-card");
    let count = 0;

    cards.forEach(function(card) {
        const text = card.innerText.toLowerCase();

        if (value === "" || text.includes(value)) {
            card.style.display = "";
            count++;
        } else {
            card.style.display = "none";
        }
    });

    document.getElementById("searchResult").textContent =
        count + " internship(s) found";
}

function applyInternship() {
    alert("This is a demo listing. Real application links will be added later.");
}
