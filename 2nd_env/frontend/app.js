const messages = document.getElementById("messages");
const form = document.getElementById("chat-form");
const input = document.getElementById("chat-input");
const statusCard = document.getElementById("status-card");

const sessionId = localStorage.getItem("ai-college-session") || crypto.randomUUID();
localStorage.setItem("ai-college-session", sessionId);

function addMessage(role, text) {
  const message = document.createElement("div");
  message.className = `message ${role}`;
  message.textContent = text;
  messages.appendChild(message);
  messages.scrollTop = messages.scrollHeight;
}

async function loadStatus() {
  try {
    const response = await fetch("/api/system/status");
    const data = await response.json();
    statusCard.innerHTML = `
      <span class="badge">Backend</span>
      <strong>${data.service === "ok" ? "Online" : "Offline"}</strong>
      <p>LLM provider: ${data.llm_provider || "unavailable"}<br>Model: ${data.ollama_model || "not configured"}<br>Simulation: ${data.simulation ? "enabled" : "disabled"}</p>
    `;
  } catch (error) {
    statusCard.innerHTML = `
      <span class="badge">Backend</span>
      <strong>Unavailable</strong>
      <p>${error.message}</p>
    `;
  }
}

async function sendMessage(message) {
  addMessage("user", message);
  addMessage("assistant", "Working...");
  const placeholder = messages.lastElementChild;
  try {
    const response = await fetch("/api/agent/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    });
    const data = await response.json();
    placeholder.textContent = data.answer;
  } catch (error) {
    placeholder.textContent = `Request failed: ${error.message}`;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const value = input.value.trim();
  if (!value) return;
  input.value = "";
  await sendMessage(value);
});

document.querySelectorAll(".quick-actions button").forEach((button) => {
  button.addEventListener("click", async () => {
    await sendMessage(button.dataset.message);
  });
});

addMessage("assistant", "Ask me for system status, a room list, or a simulated room status.");
loadStatus();
