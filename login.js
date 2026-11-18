
const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const message = document.getElementById("loginMessage");

    message.textContent = "Checking login...";
    message.style.color = "blue";

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/login",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        const result = await response.json();

        if (response.ok) {

            message.textContent =
                "Login successful! Welcome, " + result.name;

            message.style.color = "green";

            // Save student information for dashboard demo
            localStorage.setItem("studentName", result.name);
            localStorage.setItem("studentEmail", result.email);

            // Open dashboard
            setTimeout(function() {
                window.location.href = "dashboard.html";
            }, 1000);

        } else {

            message.textContent =
                result.detail || "Login failed!";

            message.style.color = "red";
        }

    } catch (error) {

        message.textContent =
            "Backend connection failed! Please check server.";

        message.style.color = "red";
    }
});
