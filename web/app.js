/**
 * Edu-Graph Assistant — Client Logic
 * Tập đoàn Nguyễn Hoàng (NHG) Design System
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const chatMessages = document.getElementById("chat-messages");
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const btnSend = document.getElementById("btn-send");
  const btnTheme = document.getElementById("btn-theme");
  const themeIcon = document.getElementById("theme-icon");
  const btnClear = document.getElementById("btn-clear");
  const welcomeHero = document.getElementById("welcome-hero");

  // Status & Metrics
  const badgeNeo4j = document.getElementById("badge-neo4j");
  const neo4jStatusText = document.getElementById("neo4j-status-text");
  const selectModel = document.getElementById("select-model");
  const valFewshot = document.getElementById("val-fewshot");
  const valRules = document.getElementById("val-rules");
  const valLatency = document.getElementById("val-latency");

  // Feedback Modal
  const modalFeedback = document.getElementById("modal-feedback");
  const fbNote = document.getElementById("fb-note");
  const fbCypher = document.getElementById("fb-cypher");
  const btnModalCancel = document.getElementById("btn-modal-cancel");
  const btnModalSubmit = document.getElementById("btn-modal-submit");

  // Toast
  const toast = document.getElementById("toast");
  const toastMsg = document.getElementById("toast-msg");
  const toastIcon = document.getElementById("toast-icon");

  let currentFeedbackContext = null;

  // ==========================================
  // 1. Theme Toggle (Light / Dark)
  // ==========================================
  const savedTheme = localStorage.getItem("nhg-theme") || "light";
  applyTheme(savedTheme);

  btnTheme.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
  });

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("nhg-theme", theme);
    themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
  }

  // ==========================================
  // 2. Fetch System Status, Models & Metrics
  // ==========================================
  async function fetchStatus() {
    try {
      const res = await fetch("/api/status");
      if (res.ok) {
        const data = await res.json();
        if (data.neo4j_connected) {
          badgeNeo4j.className = "nhg-badge online";
          neo4jStatusText.textContent = "Neo4j: Trực tuyến";
        } else {
          badgeNeo4j.className = "nhg-badge offline";
          neo4jStatusText.textContent = "Neo4j: Ngoại tuyến";
        }
        valFewshot.textContent = data.few_shot_count || "0";
        valRules.textContent = data.rules_count || "0";
      }
    } catch (err) {
      badgeNeo4j.className = "nhg-badge offline";
      neo4jStatusText.textContent = "Neo4j: Ngoại tuyến";
    }
  }

  async function loadModels() {
    try {
      const res = await fetch("/api/models");
      if (res.ok) {
        const data = await res.json();
        if (data.models && data.models.length > 0 && selectModel) {
          selectModel.innerHTML = "";
          data.models.forEach((m) => {
            const opt = document.createElement("option");
            opt.value = m.name;
            opt.textContent = m.label || m.name;
            if (m.name === data.current_model) {
              opt.selected = true;
            }
            selectModel.appendChild(opt);
          });
        }
      }
    } catch (e) {
      console.warn("Không thể tải danh sách mô hình:", e);
    }
  }

  if (selectModel) {
    selectModel.addEventListener("change", async () => {
      const chosen = selectModel.value;
      try {
        const res = await fetch("/api/model", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ model: chosen })
        });
        if (res.ok) {
          showToast("🧠", `Đã kích hoạt mô hình: ${chosen}`);
        }
      } catch (err) {
        console.error(err);
      }
    });
  }

  fetchStatus();
  loadModels();
  setInterval(fetchStatus, 15000); // Polling every 15s

  // ==========================================
  // 3. Chat Interaction & Messaging
  // ==========================================
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;
    sendMessage(query);
  });

  // Auto-resize textarea & Enter key to send
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  chatInput.addEventListener("input", () => {
    chatInput.style.height = "24px";
    chatInput.style.height = Math.min(chatInput.scrollHeight, 140) + "px";
  });

  // Quick Chips click
  document.querySelectorAll(".nhg-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const prompt = chip.getAttribute("data-prompt");
      if (prompt) {
        chatInput.value = prompt;
        sendMessage(prompt);
      }
    });
  });

  // Clear Chat
  btnClear.addEventListener("click", () => {
    chatMessages.innerHTML = "";
    if (welcomeHero) {
      chatMessages.appendChild(welcomeHero);
    }
  });

  async function sendMessage(question) {
    if (welcomeHero && welcomeHero.parentNode === chatMessages) {
      welcomeHero.remove();
    }

    // Render User Message
    appendUserMessage(question);
    chatInput.value = "";
    chatInput.style.height = "24px";
    btnSend.disabled = true;

    // Render Typing Indicator with live timer
    const typingRow = appendTypingIndicator();
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const selectedModel = selectModel ? selectModel.value : null;

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, model: selectedModel })
      });

      if (typingRow._timerInterval) {
        clearInterval(typingRow._timerInterval);
      }
      typingRow.remove();

      if (response.ok) {
        const data = await response.json();
        appendAssistantMessage(data);
      } else {
        const errData = await response.json().catch(() => ({}));
        appendErrorMessage(errData.error || "Không thể xử lý yêu cầu lúc này.");
      }
    } catch (err) {
      if (typingRow._timerInterval) {
        clearInterval(typingRow._timerInterval);
      }
      typingRow.remove();
      appendErrorMessage("Lỗi kết nối máy chủ dịch vụ.");
    } finally {
      btnSend.disabled = false;
      chatInput.focus();
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  function appendUserMessage(text) {
    const row = document.createElement("div");
    row.className = "nhg-message-row user";
    row.innerHTML = `
      <div class="nhg-avatar user">👤</div>
      <div class="nhg-bubble">${escapeHtml(text)}</div>
    `;
    chatMessages.appendChild(row);
  }

  function appendTypingIndicator() {
    const row = document.createElement("div");
    row.className = "nhg-message-row assistant";
    row.innerHTML = `
      <div class="nhg-avatar assistant">AI</div>
      <div class="nhg-bubble">
        <div class="nhg-typing-indicator">
          <span style="font-size: 13px; color: var(--nhg-text-secondary); margin-right: 8px;">
            Đang phân tích đồ thị và sinh Cypher... <span class="nhg-live-timer">(0.0s)</span>
          </span>
          <div class="nhg-dot"></div>
          <div class="nhg-dot"></div>
          <div class="nhg-dot"></div>
        </div>
      </div>
    `;
    chatMessages.appendChild(row);

    const timerSpan = row.querySelector(".nhg-live-timer");
    const startTime = performance.now();
    const timerInterval = setInterval(() => {
      const sec = ((performance.now() - startTime) / 1000).toFixed(1);
      if (timerSpan) {
        timerSpan.textContent = `(${sec}s)`;
      }
    }, 100);

    row._timerInterval = timerInterval;
    return row;
  }

  function appendAssistantMessage(data) {
    const row = document.createElement("div");
    row.className = "nhg-message-row assistant";

    const intentTag = data.intent ? `<span class="nhg-agent-pill">🎯 Intent: ${data.intent}</span>` : "";
    const recordCount = data.count !== undefined ? `<span>${data.count} kết quả</span>` : "";

    // Parse latency breakdown
    let latencyBadge = "";
    if (data.latency) {
      const lat = data.latency;
      const totalSec = lat.total_seconds || (lat.total_ms / 1000).toFixed(2);
      const modelLabel = data.model || "OLM";
      latencyBadge = `
        <span class="nhg-latency-pill" title="Tổng: ${totalSec}s | Router: ${lat.router_ms}ms | Cypher OLM: ${lat.cypher_ms}ms | Neo4j: ${lat.neo4j_ms}ms | Reporter: ${lat.reporter_ms}ms">
          ⚡ ${totalSec}s • ${modelLabel}
        </span>
      `;
      if (valLatency) {
        valLatency.textContent = `${totalSec}s`;
      }
    }

    // Parse data table if records exist
    let tableHtml = "";
    let warningAlertHtml = "";

    if (data.records && data.records.length > 0) {
      const headers = Object.keys(data.records[0]);
      let rowsHtml = "";
      let hasWarning = false;

      data.records.forEach((rec) => {
        let isRowWarning = false;
        let cells = headers
          .map((h) => {
            const val = rec[h] !== null && rec[h] !== undefined ? rec[h] : "-";
            if (h.toLowerCase().includes("absent") && typeof val === "number" && val >= 20.0) {
              isRowWarning = true;
              hasWarning = true;
            }
            return `<td>${escapeHtml(String(val))}</td>`;
          })
          .join("");

        rowsHtml += `<tr class="${isRowWarning ? "nhg-row-warning" : ""}">${cells}</tr>`;
      });

      tableHtml = `
        <div class="nhg-table-wrapper">
          <table class="nhg-data-table">
            <thead>
              <tr>${headers.map((h) => `<th>${escapeHtml(h)}</th>`).join("")}</tr>
            </thead>
            <tbody>${rowsHtml}</tbody>
          </table>
        </div>
      `;

      if (hasWarning) {
        warningAlertHtml = `
          <div class="nhg-alert-box">
            <span>🚨</span>
            <div><strong>Cảnh báo học vụ:</strong> Phát hiện sinh viên có tỷ lệ vắng vượt ngưỡng quy định 20% (nguy cơ cấm thi)!</div>
          </div>
        `;
      }
    } else if (data.success && (!data.records || data.records.length === 0)) {
      tableHtml = `<p style="margin: 8px 0; color: var(--nhg-text-secondary);">ℹ️ Không tìm thấy bản ghi nào phù hợp trong cơ sở dữ liệu.</p>`;
    } else if (!data.success) {
      tableHtml = `<div class="nhg-alert-box"><span>⚠️</span><div>${escapeHtml(data.error || "Không thể thực thi truy vấn.")}</div></div>`;
    }

    // Cypher Accordion
    const cypherSnippet = data.cypher
      ? `
      <details class="nhg-cypher-accordion">
        <summary class="nhg-cypher-summary">
          <span>🔍 Mã Cypher Thực Thi</span>
          <span style="font-size: 11px; opacity: 0.8;">Bấm để xem</span>
        </summary>
        <pre class="nhg-cypher-code">${escapeHtml(data.cypher)}</pre>
      </details>
    `
      : "";

    // Feedback Action Bar
    const feedbackBar = `
      <div class="nhg-feedback-bar">
        <span style="font-size: 11px; color: var(--nhg-text-tertiary); margin-right: auto;">Đánh giá để OLM tự học:</span>
        <button class="nhg-feedback-btn up" title="Câu trả lời đúng">👍 Đúng</button>
        <button class="nhg-feedback-btn down" title="Cần điều chỉnh / Chưa đúng">👎 Chưa đúng</button>
      </div>
    `;

    row.innerHTML = `
      <div class="nhg-avatar assistant">AI</div>
      <div class="nhg-bubble">
        <div class="nhg-bubble-meta">
          ${intentTag}
          ${recordCount}
          ${latencyBadge}
        </div>
        ${warningAlertHtml}
        ${tableHtml}
        ${cypherSnippet}
        ${feedbackBar}
      </div>
    `;

    chatMessages.appendChild(row);

    // Bind Feedback Buttons
    const btnUp = row.querySelector(".nhg-feedback-btn.up");
    const btnDown = row.querySelector(".nhg-feedback-btn.down");

    btnUp.addEventListener("click", () => {
      sendFeedback(data.question, data.cypher, true);
      btnUp.classList.add("active");
      btnDown.classList.remove("active");
      showToast("Cảm ơn bạn! Đã lưu câu hỏi vào Kho Ví Dụ Mẫu.", "👍");
    });

    btnDown.addEventListener("click", () => {
      currentFeedbackContext = {
        question: data.question,
        cypher: data.cypher,
        btnUp,
        btnDown
      };
      fbNote.value = "";
      fbCypher.value = data.cypher || "";
      modalFeedback.classList.add("active");
    });
  }

  function appendErrorMessage(msg) {
    const row = document.createElement("div");
    row.className = "nhg-message-row assistant";
    row.innerHTML = `
      <div class="nhg-avatar assistant">AI</div>
      <div class="nhg-bubble">
        <div class="nhg-alert-box">
          <span>❌</span>
          <div>${escapeHtml(msg)}</div>
        </div>
      </div>
    `;
    chatMessages.appendChild(row);
  }

  // ==========================================
  // 4. Modal & Feedback Handling
  // ==========================================
  btnModalCancel.addEventListener("click", () => {
    modalFeedback.classList.remove("active");
  });

  btnModalSubmit.addEventListener("click", () => {
    if (!currentFeedbackContext) return;

    const note = fbNote.value.trim();
    const corrected = fbCypher.value.trim();

    sendFeedback(currentFeedbackContext.question, currentFeedbackContext.cypher, false, note, corrected);

    currentFeedbackContext.btnDown.classList.add("active");
    currentFeedbackContext.btnUp.classList.remove("active");
    modalFeedback.classList.remove("active");

    showToast("Đã ghi nhận quy tắc nghiệp vụ vào Sổ Tay OLM!", "🎯");
    fetchStatus(); // Refresh rule counter
  });

  async function sendFeedback(question, cypher, isCorrect, note = null, correctedCypher = null) {
    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          cypher,
          is_correct: isCorrect,
          note,
          corrected_cypher: correctedCypher
        })
      });
      fetchStatus();
    } catch (err) {
      console.error("Lỗi gửi feedback:", err);
    }
  }

  function showToast(message, icon = "✅") {
    toastMsg.textContent = message;
    toastIcon.textContent = icon;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 3500);
  }

  function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
});
