const messageListEl = document.getElementById("message-list");
const totalCountEl = document.getElementById("total-count");
const unreadCountEl = document.getElementById("unread-count");

function formatDate(isoString) {
  const date = new Date(isoString.replace(" ", "T") + "Z");
  if (isNaN(date.getTime())) return isoString;
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function renderMessages(messages) {
  if (messages.length === 0) {
    messageListEl.innerHTML = '<div class="empty-state">No messages yet.</div>';
    return;
  }

  messageListEl.innerHTML = messages
    .map((msg) => {
      const unreadClass = msg.is_read ? "" : "unread";
      const badgeClass = msg.is_read ? "read" : "unread";
      const badgeText = msg.is_read ? "Read" : "Unread";

      return `
        <div class="message-card ${unreadClass}" data-id="${msg.id}">
          <div class="message-card-header">
            <span class="message-username">${escapeHtml(msg.username)}</span>
            <span class="status-badge ${badgeClass}">${badgeText}</span>
          </div>
          <div class="message-body">${escapeHtml(msg.message)}</div>
          <div class="message-card-header">
            <span class="message-date">${formatDate(msg.created_at)}</span>
            <div class="message-actions">
              ${!msg.is_read ? `<button class="btn btn-secondary btn-small mark-read-btn" data-id="${msg.id}">Mark as Read</button>` : ""}
              <button class="btn btn-danger btn-small delete-btn" data-id="${msg.id}">Delete</button>
            </div>
          </div>
        </div>
      `;
    })
    .join("");

  document.querySelectorAll(".mark-read-btn").forEach((btn) => {
    btn.addEventListener("click", () => markAsRead(btn.dataset.id));
  });

  document.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", () => deleteMessage(btn.dataset.id));
  });
}

async function loadMessages() {
  try {
    const response = await fetch("/api/messages");

    if (response.status === 401) {
      window.location.href = "/admin/login";
      return;
    }

    const data = await response.json();

    totalCountEl.textContent = data.total_count;
    unreadCountEl.textContent = data.unread_count;
    renderMessages(data.messages);
  } catch (err) {
    messageListEl.innerHTML = '<div class="empty-state">Failed to load messages. Please refresh the page.</div>';
  }
}

async function markAsRead(id) {
  try {
    const response = await fetch(`/api/messages/${id}/read`, { method: "PATCH" });
    if (response.ok) {
      loadMessages();
    }
  } catch (err) {
    console.error("Failed to mark message as read", err);
  }
}

async function deleteMessage(id) {
  if (!confirm("Are you sure you want to delete this message? This cannot be undone.")) {
    return;
  }

  try {
    const response = await fetch(`/api/messages/${id}`, { method: "DELETE" });
    if (response.ok) {
      loadMessages();
    }
  } catch (err) {
    console.error("Failed to delete message", err);
  }
}

loadMessages();
