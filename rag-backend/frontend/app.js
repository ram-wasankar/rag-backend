const API_BASE = "";

const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const dropzone = document.getElementById("dropzone");
const fileName = document.getElementById("file-name");
const uploadStatus = document.getElementById("upload-status");

const queryForm = document.getElementById("query-form");
const queryInput = document.getElementById("query-input");
const answerEl = document.getElementById("answer");
const chunksEl = document.getElementById("chunks");

function setStatus(element, message, type) {
  element.textContent = message;
  element.classList.remove("ok", "error");
  if (type) {
    element.classList.add(type);
  }
}

function setFileName() {
  const file = fileInput.files && fileInput.files[0];
  fileName.textContent = file ? file.name : "No file selected";
}

["dragenter", "dragover"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    dropzone.classList.add("is-dragover");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropzone.addEventListener(eventName, (event) => {
    event.preventDefault();
    event.stopPropagation();
    dropzone.classList.remove("is-dragover");
  });
});

dropzone.addEventListener("drop", (event) => {
  const files = event.dataTransfer.files;
  if (files && files.length) {
    fileInput.files = files;
    setFileName();
  }
});

fileInput.addEventListener("change", setFileName);

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = fileInput.files && fileInput.files[0];
  if (!file) {
    setStatus(uploadStatus, "Please select a file first.", "error");
    return;
  }

  const button = uploadForm.querySelector("button");
  button.disabled = true;
  setStatus(uploadStatus, "Uploading and indexing...", null);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Upload failed");
    }

    setStatus(
      uploadStatus,
      `Indexed ${payload.chunks_added} chunks from ${payload.source}.`,
      "ok"
    );
  } catch (error) {
    setStatus(uploadStatus, error.message || "Upload failed.", "error");
  } finally {
    button.disabled = false;
  }
});

queryForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = queryInput.value.trim();
  if (!query) {
    answerEl.textContent = "Add a query to search.";
    return;
  }

  const button = queryForm.querySelector("button");
  button.disabled = true;
  answerEl.textContent = "Searching...";
  chunksEl.innerHTML = "";

  try {
    const response = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.detail || "Query failed");
    }

    answerEl.textContent = payload.answer || "Not found";
    renderChunks(payload.chunks || []);
  } catch (error) {
    answerEl.textContent = error.message || "Query failed.";
  } finally {
    button.disabled = false;
  }
});

function renderChunks(chunks) {
  if (!chunks.length) {
    chunksEl.innerHTML = "<p class=\"muted\">No chunks returned.</p>";
    return;
  }

  const elements = chunks.map((chunk) => {
    const score = typeof chunk.score === "number" ? chunk.score.toFixed(3) : "-";
    return `
      <article class="chunk">
        <div class="chunk__meta">
          <span>Source: ${chunk.source || "unknown"}</span>
          <span>Score: ${score}</span>
          <span>ID: ${chunk.id}</span>
        </div>
        <div>${escapeHtml(chunk.text || "")}</div>
      </article>
    `;
  });

  chunksEl.innerHTML = elements.join("");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
