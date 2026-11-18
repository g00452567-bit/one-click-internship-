
const registrationForm = document.getElementById("registrationForm");

registrationForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const name = document.getElementById("fullName").value.trim();
    const email = document.getElementById("email").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const college = document.getElementById("college").value.trim();
    const course = document.getElementById("course").value.trim();
    const year = document.getElementById("year").value;
    const skills = document.getElementById("skills").value.trim();
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const message = document.getElementById("registrationMessage");

    if (!/^\d{10}$/.test(phone)) {
        message.textContent = "Enter a valid 10-digit mobile number!";
        message.style.color = "red";
        return;
    }

    if (password.length < 8) {
        message.textContent = "Password must contain at least 8 characters!";
        message.style.color = "red";
        return;
    }

    if (password !== confirmPassword) {
        message.textContent = "Passwords do not match!";
        message.style.color = "red";
        return;
    }

    message.textContent = "Registering...";
    message.style.color = "blue";

    try {
        const response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name, email, phone, college,
                course, year, skills, password
            })
        });

        const result = await response.json();

        if (response.ok) {
            message.textContent = "Registration Successful!";
            message.style.color = "green";
            registrationForm.reset();
        } else {
            message.textContent = result.detail || "Registration failed!";
            message.style.color = "red";
        }

    } catch (error) {
        message.textContent = "Backend connection failed. Check your server.";
        message.style.color = "red";
    }
});
