const messagesEl = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const uploadForm = document.getElementById("upload-form");
const messageInput = document.getElementById("message-input");
const imageInput = document.getElementById("image-input");
const fileInput = document.getElementById("file-input");
const imagePreview = document.getElementById("image-preview");
const analysisOutput = document.getElementById("analysis-output");
const healthBadge = document.getElementById("health-badge");
const reasoningModelSelect = document.getElementById("reasoning-model");
const visionModelSelect = document.getElementById("vision-model");
const modeSelect = document.getElementById("mode");
const sendBtn = document.getElementById("send-btn");
const uploadBtn = document.getElementById("upload-btn");

let selectedImage = null;

function addMessage(text, role = "assistant") {
  const node = document.createElement("div");
  node.className = `message ${role}`;
  node.textContent = text;
  messagesEl.appendChild(node);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function renderAnalysis(analysis) {
  const sections = [
    ["Summary", analysis.analysis],
    ["Name", analysis.name],
    ["Description", analysis.description],
    ["Terms", analysis.terms],
    ["Conditions", analysis.conditions],
    ["Liabilities", analysis.liabilities],
    ["Rights", analysis.rights],
    ["Obligations", analysis.obligations],
    ["Guarantees", analysis.guarantees],
    ["Warranties", analysis.warranties],
  ];

  analysisOutput.innerHTML = sections
    .map(([title, value]) => {
      if (Array.isArray(value)) {
        const items = value.map((item) => `<li>${item}</li>`).join("");
        return `<div class="analysis-section"><h3>${title}</h3><ul>${items}</ul></div>`;
      }
      return `<div class="analysis-section"><h3>${title}</h3><p>${value}</p></div>`;
    })
    .join("");
}

async function loadModels() {
  const response = await fetch("/llm/models");
  const data = await response.json();

  reasoningModelSelect.innerHTML = data.reasoning_models
    .map(
      (model) =>
        `<option value="${model}" ${
          model === data.default_reasoning_model ? "selected" : ""
        }>${model}</option>`
    )
    .join("");

  visionModelSelect.innerHTML = data.vision_models
    .map(
      (model) =>
        `<option value="${model}" ${
          model === data.default_vision_model ? "selected" : ""
        }>${model}</option>`
    )
    .join("");
}

async function checkHealth() {
  try {
    const response = await fetch("/llm/health");
    const data = await response.json();

    if (data.status === "ok") {
      healthBadge.textContent = `Ollama connected (${data.installed_models.length} models)`;
      healthBadge.className = "badge badge-ok";
      return;
    }

    healthBadge.textContent = `LLM status: ${data.status}`;
    healthBadge.className = "badge badge-error";
  } catch (error) {
    healthBadge.textContent = "LLM unreachable";
    healthBadge.className = "badge badge-error";
  }
}

imageInput.addEventListener("change", () => {
  selectedImage = imageInput.files?.[0] || null;
  imagePreview.innerHTML = "";

  if (!selectedImage) {
    imagePreview.classList.add("hidden");
    return;
  }

  const img = document.createElement("img");
  img.src = URL.createObjectURL(selectedImage);
  imagePreview.appendChild(img);
  imagePreview.classList.remove("hidden");
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message && !selectedImage) {
    return;
  }

  addMessage(message || "[Image attached]", "user");
  sendBtn.disabled = true;
  sendBtn.textContent = "Thinking...";

  try {
    const formData = new FormData();
    formData.append("message", message || "Analyze this contract.");
    formData.append("mode", modeSelect.value);
    formData.append("model", reasoningModelSelect.value);
    formData.append("vision_model", visionModelSelect.value);
    if (selectedImage) {
      formData.append("image", selectedImage);
    }

    const response = await fetch("/chat", { method: "POST", body: formData });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed");
    }

    if (data.mode === "chat") {
      addMessage(data.response, "assistant");
    } else {
      addMessage(
        `Analysis complete using ${data.model_used}${
          data.vision_model_used ? ` + ${data.vision_model_used}` : ""
        }.`,
        "assistant"
      );
      renderAnalysis(data.analysis);
    }

    messageInput.value = "";
    selectedImage = null;
    imageInput.value = "";
    imagePreview.classList.add("hidden");
    imagePreview.innerHTML = "";
  } catch (error) {
    addMessage(`Error: ${error.message}`, "assistant");
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Send";
  }
});

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = fileInput.files?.[0];
  if (!file) {
    return;
  }

  uploadBtn.disabled = true;
  uploadBtn.textContent = "Analyzing...";

  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", reasoningModelSelect.value);

    const response = await fetch("/contracts/upload", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Upload failed");
    }

    addMessage(`Analyzed uploaded file: ${file.name}`, "assistant");
    renderAnalysis(data);
  } catch (error) {
    addMessage(`Upload error: ${error.message}`, "assistant");
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.textContent = "Analyze file";
  }
});

loadModels();
checkHealth();
