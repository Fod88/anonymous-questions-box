// ---------------------------------------------------------------------------
// Welcome page: toggle between Anonymous / Username mode
// ---------------------------------------------------------------------------
(function initWelcomePage() {
  const anonymousOption = document.getElementById("option-anonymous");
  const usernameOption = document.getElementById("option-username");
  const usernameField = document.getElementById("username-field");
  const usernameInput = document.getElementById("username");

  if (!anonymousOption || !usernameOption) return;

  function setMode(mode) {
    if (mode === "username") {
      usernameOption.classList.add("active");
      anonymousOption.classList.remove("active");
      usernameField.classList.add("visible");
    } else {
      anonymousOption.classList.add("active");
      usernameOption.classList.remove("active");
      usernameField.classList.remove("visible");
      usernameInput.value = "";
    }
  }

  anonymousOption.addEventListener("click", () => setMode("anonymous"));
  usernameOption.addEventListener("click", () => setMode("username"));
})();

// ---------------------------------------------------------------------------
// Messages page: send a message via the API
// ---------------------------------------------------------------------------
(function initMessagesPage() {
  const form = document.getElementById("message-form");
  if (!form) return;

  const textarea = document.getElementById("message");
  const alertBox = document.getElementById("alert-box");
  const sendBtn = document.getElementById("send-btn");

  function showAlert(text, type) {
    alertBox.innerHTML = `<div class="alert alert-${type}">${text}</div>`;
  }

  function clearAlert() {
    alertBox.innerHTML = "";
  }

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    clearAlert();

    const message = textarea.value.trim();
    if (!message) {
      showAlert("Please write a message before sending.", "error");
      return;
    }

    sendBtn.disabled = true;
    sendBtn.textContent = "Sending...";

    try {
      const response = await fetch("/api/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: message,
          username: window.CURRENT_USERNAME || "Anonymous",
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        showAlert(data.error || "Something went wrong. Please try again.", "error");
      } else {
        showAlert("Your message has been sent successfully! You can send another message anytime.", "success");
        textarea.value = "";
      }
    } catch (err) {
      showAlert("Network error. Please check your connection and try again.", "error");
    } finally {
      sendBtn.disabled = false;
      sendBtn.textContent = "Send Message";
    }
  });
})();
