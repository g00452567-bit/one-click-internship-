
const loginForm = document.getElementById("loginForm");

if (loginForm) {
    loginForm.addEventListener("submit", async function(event) {
        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;
        const message = document.getElementById("loginMessage");

        message.textContent = "Checking login...";
        message.style.color = "blue";

        try {
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });

            const result = await response.json();

            if (response.ok) {
                message.textContent =
                    "Login successful! Welcome, " + result.name;

                message.style.color = "green";

                localStorage.setItem("studentName", result.name);
                localStorage.setItem("studentEmail", result.email);

                setTimeout(function() {
                    window.location.href = "dashboard.html";
                }, 1000);

            } else {
                message.textContent =
                    result.detail || "Login failed!";

                message.style.color = "red";
            }

        } catch (error) {
            console.error("Login error:", error);

            message.textContent =
                "Backend connection failed! Please try again.";

            message.style.color = "red";
        }
    });
}
