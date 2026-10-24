/**
 * app.js
 * ------
 * Client-side logic for AMC CivicAI — Nagarik Redressal Portal.
 *
 * Responsibilities:
 *   - SPA page navigation (Report / Track / Directory).
 *   - Image upload with drag-and-drop and file browser.
 *   - Complaint filing via the agent pipeline API.
 *   - Animated tool-step execution trace rendering.
 *   - Ticket tracking via status lookup API.
 *   - Ward & department directory rendering.
 *   - Chat widget with grounded civic responses.
 *   - Scenario quick-fill for demo convenience.
 *   - Screen reader announcements via aria-live region.
 */

"use strict";

// ── DOM Cache ───────────────────────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const DOM = {
    // Navigation
    navLinks: $$(".nav-link[data-page]"),
    pages: $$(".page-section"),
    // Report page
    form: $("#complaint-form"),
    formError: $("#form-error"),
    citizenName: $("#citizen-name"),
    citizenPhone: $("#citizen-phone"),
    areaAddress: $("#area-address"),
    description: $("#description"),
    submitBtn: $("#submit-btn"),
    btnText: $("#btn-text"),
    btnSpinner: $("#btn-spinner"),
    // Image
    fileInput: $("#file-input"),
    imageContainer: $("#image-container"),
    imagePlaceholder: $("#image-placeholder"),
    previewImage: $("#preview-image"),
    confidenceBadge: $("#confidence-badge"),
    filenameDisplay: $("#filename-display"),
    btnBrowse: $("#btn-browse"),
    btnRetake: $("#btn-retake"),
    gpsAddress: $("#gps-address"),
    gpsCoords: $("#gps-coords"),
    // Pipeline
    pipelineBadge: $("#pipeline-badge"),
    ticketResult: $("#ticket-result"),
    resultTicketId: $("#result-ticket-id"),
    resultSla: $("#result-sla"),
    btnCopyId: $("#btn-copy-id"),
    btnTrackTicket: $("#btn-track-ticket"),
    // Scenario chips
    scenarioChips: $$(".scenario-chip"),
    // Track page
    trackInput: $("#track-input"),
    btnTrack: $("#btn-track"),
    trackResult: $("#track-result"),
    trackEmpty: $("#track-empty"),
    // Directory page
    wardGrid: $("#ward-grid"),
    deptGrid: $("#dept-grid"),
    // Chat
    chatToggle: $("#chat-toggle-btn"),
    chatWidget: $("#chat-widget"),
    chatClose: $("#chat-close-btn"),
    chatForm: $("#chat-form"),
    chatInput: $("#chat-input"),
    chatFeed: $("#chat-feed"),
    chatChips: $$(".chat-chip"),
    // Accessibility
    announcer: $("#sr-announcer"),
};

// ── State ───────────────────────────────────────────────────────────────────
let uploadedFile = null;
let lastTicketId = null;

// ── Scenario Data ───────────────────────────────────────────────────────────
const SCENARIOS = {
    pothole: {
        name: "Keval M. Shah",
        phone: "9825012345",
        area: "Pakwan Cross Road, SG Highway, Bodakdev",
        desc: "Deep pothole damaging two-wheelers during evening rush hour near service lane.",
        filename: "pothole_sg_highway_bodakdev.jpg",
        gpsAddr: "Pakwan Crossroad, SG Highway, Bodakdev",
        gpsCoords: "23.0487° N, 72.5074° E",
    },
    pipe_burst: {
        name: "Priya R. Desai",
        phone: "9876543210",
        area: "C.G. Road, near Gujarat University, Navrangpura",
        desc: "Major water pipe burst flooding the road for over 2 hours. Traffic completely blocked.",
        filename: "pipe_burst_navrangpura_cg_road.jpg",
        gpsAddr: "C.G. Road, Navrangpura",
        gpsCoords: "23.0350° N, 72.5610° E",
    },
    garbage_dump: {
        name: "Amit B. Patel",
        phone: "8765432109",
        area: "Kankaria Lake Gate 1-4, Maninagar",
        desc: "Large garbage dump near residential area. Foul smell and mosquito breeding risk.",
        filename: "garbage_dump_maninagar_kankaria.jpg",
        gpsAddr: "Kankaria Lake, Maninagar",
        gpsCoords: "23.0070° N, 72.6040° E",
    },
    streetlight_off: {
        name: "Sneha K. Joshi",
        phone: "7654321098",
        area: "Thaltej Cross Road, Hebatpur Road, Thaltej",
        desc: "Row of 5 streetlights non-functional for over a week. Dangerous after dark.",
        filename: "streetlight_off_thaltej_crossroad.jpg",
        gpsAddr: "Thaltej Cross Road, Thaltej",
        gpsCoords: "23.0569° N, 72.4967° E",
    },
};

// ── Utility Functions ───────────────────────────────────────────────────────

function announce(text) {
    if (DOM.announcer) {
        DOM.announcer.textContent = text;
    }
}

function showFormError(msg) {
    DOM.formError.textContent = msg;
    DOM.formError.classList.add("visible");
}

function hideFormError() {
    DOM.formError.classList.remove("visible");
    DOM.formError.textContent = "";
}

function setLoading(isLoading) {
    DOM.submitBtn.disabled = isLoading;
    DOM.btnText.textContent = isLoading ? "Processing..." : "▶ Submit Grievance & Get Updates";
    if (isLoading) {
        DOM.btnSpinner.classList.add("visible");
    } else {
        DOM.btnSpinner.classList.remove("visible");
    }
}

// ── Page Navigation ─────────────────────────────────────────────────────────

function navigateTo(page) {
    DOM.navLinks.forEach((link) => {
        link.classList.toggle("active", link.dataset.page === page);
    });
    DOM.pages.forEach((section) => {
        const id = section.id.replace("page-", "");
        if (id === page) {
            section.classList.remove("d-none");
            section.classList.add("fade-in");
        } else {
            section.classList.add("d-none");
        }
    });
    announce(`Navigated to ${page} page`);
    window.scrollTo({ top: 0, behavior: "smooth" });
}

DOM.navLinks.forEach((link) => {
    link.addEventListener("click", () => navigateTo(link.dataset.page));
});

// Brand logo → Report page
if ($("#brand-link")) {
    $("#brand-link").addEventListener("click", (e) => {
        e.preventDefault();
        navigateTo("report");
    });
}

// ── Scenario Quick-Fill ─────────────────────────────────────────────────────

DOM.scenarioChips.forEach((chip) => {
    chip.addEventListener("click", () => {
        const key = chip.dataset.scenario;
        const data = SCENARIOS[key];
        if (!data) return;

        // Update active chip
        DOM.scenarioChips.forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");

        // Fill form
        DOM.citizenName.value = data.name;
        DOM.citizenPhone.value = data.phone;
        DOM.areaAddress.value = data.area;
        DOM.description.value = data.desc;
        DOM.gpsAddress.textContent = data.gpsAddr;
        DOM.gpsCoords.textContent = data.gpsCoords;
        DOM.filenameDisplay.textContent = data.filename;

        // Reset pipeline
        resetPipeline();

        announce(`Loaded scenario: ${chip.textContent.trim()}`);
    });
});

// ── Image Upload ────────────────────────────────────────────────────────────

function handleImageUpload(file) {
    if (!file) return;

    const validTypes = ["image/jpeg", "image/png", "image/webp"];
    if (!validTypes.includes(file.type)) {
        showFormError("Invalid file type. Please upload JPG, PNG, or WebP.");
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showFormError("File too large. Maximum size is 10MB.");
        return;
    }

    hideFormError();
    uploadedFile = file;
    DOM.filenameDisplay.textContent = file.name;

    const reader = new FileReader();
    reader.onload = (e) => {
        DOM.previewImage.src = e.target.result;
        DOM.previewImage.classList.remove("d-none");
        DOM.imagePlaceholder.classList.add("d-none");
        DOM.confidenceBadge.classList.remove("d-none");
    };
    reader.readAsDataURL(file);

    announce(`Image uploaded: ${file.name}`);
}

DOM.fileInput.addEventListener("change", (e) => {
    handleImageUpload(e.target.files[0]);
});

DOM.imagePlaceholder.addEventListener("click", () => DOM.fileInput.click());
DOM.imagePlaceholder.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        DOM.fileInput.click();
    }
});
DOM.btnBrowse.addEventListener("click", () => DOM.fileInput.click());
DOM.btnRetake.addEventListener("click", () => {
    uploadedFile = null;
    DOM.fileInput.value = "";
    DOM.previewImage.classList.add("d-none");
    DOM.previewImage.src = "";
    DOM.imagePlaceholder.classList.remove("d-none");
    DOM.confidenceBadge.classList.add("d-none");
    DOM.filenameDisplay.textContent = "No file selected";
});

// Drag and drop
DOM.imageContainer.addEventListener("dragover", (e) => {
    e.preventDefault();
    DOM.imageContainer.style.borderColor = "var(--primary)";
});
DOM.imageContainer.addEventListener("dragleave", () => {
    DOM.imageContainer.style.borderColor = "";
});
DOM.imageContainer.addEventListener("drop", (e) => {
    e.preventDefault();
    DOM.imageContainer.style.borderColor = "";
    const file = e.dataTransfer.files[0];
    if (file) handleImageUpload(file);
});

// ── Pipeline Rendering ──────────────────────────────────────────────────────

function resetPipeline() {
    for (let i = 1; i <= 4; i++) {
        const step = $(`#step-${i}`);
        step.className = "tool-step pending";
        $(`#step-${i}-latency`).textContent = "—";
        $(`#step-${i}-status`).textContent = "PENDING";
        $(`#step-${i}-status`).className = "status-badge pending";
        $(`#step-${i}-body`).innerHTML = "";
    }
    DOM.pipelineBadge.textContent = "Awaiting Input";
    DOM.pipelineBadge.className = "execution-badge pending";
    DOM.ticketResult.classList.add("d-none");
}

async function animateStep(stepNum, traceItem) {
    const step = $(`#step-${stepNum}`);
    const latency = $(`#step-${stepNum}-latency`);
    const status = $(`#step-${stepNum}-status`);
    const body = $(`#step-${stepNum}-body`);

    // Active state
    step.className = "tool-step active";
    status.textContent = "RUNNING";
    status.className = "status-badge pending";

    // Simulate processing delay for visual effect
    await new Promise((r) => setTimeout(r, 400 + Math.random() * 300));

    // Completed state
    step.className = "tool-step completed";
    latency.textContent = `${traceItem.latency_ms}ms`;
    status.textContent = "✓ SUCCESS";
    status.className = "status-badge success";

    // Render result grid
    const result = traceItem.result;
    if (result) {
        let html = '<div class="tool-result-grid">';
        for (const [key, val] of Object.entries(result)) {
            const displayKey = key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
            let valClass = "";
            if (key === "urgency" && (val === "URGENT" || val === "CRITICAL")) valClass = "urgent";
            if (key === "status" && val === "assigned") valClass = "success";
            if (key === "confidence") {
                html += `<div class="tool-result-item"><div class="label">${displayKey}</div><div class="value success">${(val * 100).toFixed(1)}%</div></div>`;
            } else {
                html += `<div class="tool-result-item"><div class="label">${displayKey}</div><div class="value ${valClass}">${val}</div></div>`;
            }
        }
        html += "</div>";
        body.innerHTML = html;
    }

    announce(`Step ${stepNum} completed: ${traceItem.description}`);
}

function showTicketResult(response) {
    DOM.ticketResult.classList.remove("d-none");
    DOM.resultTicketId.textContent = `#${response.ticket_id}`;
    DOM.resultSla.textContent = `⏱ SLA: ${response.sla_hours} Hours (${response.department?.urgency || "NORMAL"})`;
    lastTicketId = response.ticket_id;

    DOM.pipelineBadge.textContent = `Execution: ${response.agent_trace.reduce((s, t) => s + t.latency_ms, 0)}ms`;
    DOM.pipelineBadge.className = "execution-badge";

    announce(`Ticket created: ${response.ticket_id}. SLA: ${response.sla_hours} hours.`);
}

// ── Complaint Submission ────────────────────────────────────────────────────

DOM.form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideFormError();

    const name = DOM.citizenName.value.trim();
    const phone = DOM.citizenPhone.value.trim();
    const area = DOM.areaAddress.value.trim();
    const desc = DOM.description.value.trim();

    // Client-side validation
    if (!name || !phone || !area) {
        showFormError("Please fill in all required fields (Name, Phone, Area).");
        return;
    }
    if (!/^\+?[0-9]{10,15}$/.test(phone)) {
        showFormError("Invalid phone number. Please enter a 10-15 digit number.");
        return;
    }

    setLoading(true);
    resetPipeline();
    DOM.pipelineBadge.textContent = "Executing...";
    DOM.pipelineBadge.className = "execution-badge";

    try {
        // Determine which endpoint to use
        let response;

        if (uploadedFile) {
            // Use multipart form upload
            const formData = new FormData();
            formData.append("citizen_name", name);
            formData.append("phone", phone);
            formData.append("area_or_address", area);
            formData.append("description", desc);
            formData.append("image", uploadedFile);

            const res = await fetch("/complaint/file-with-image", {
                method: "POST",
                body: formData,
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `Server error: ${res.status}`);
            }
            response = await res.json();
        } else {
            // Use JSON body
            const activeScenario = document.querySelector(".scenario-chip.active");
            const issueType = activeScenario ? activeScenario.dataset.scenario : null;

            const payload = {
                citizen_name: name,
                phone: phone,
                area_or_address: area,
                description: desc,
            };
            if (issueType) payload.issue_type = issueType;

            const res = await fetch("/complaint/file", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `Server error: ${res.status}`);
            }
            response = await res.json();
        }

        // Animate the pipeline steps sequentially
        if (response.agent_trace) {
            for (const trace of response.agent_trace) {
                await animateStep(trace.step, trace);
            }
        }

        showTicketResult(response);

        // Update confidence badge if we have image analysis
        if (response.image_analysis) {
            DOM.confidenceBadge.textContent = `✓ AI Visual Confidence ${(response.image_analysis.confidence * 100).toFixed(1)}%`;
            DOM.confidenceBadge.classList.remove("d-none");
        }

    } catch (err) {
        showFormError(err.message || "Failed to submit complaint. Please try again.");
        DOM.pipelineBadge.textContent = "Error";
        DOM.pipelineBadge.className = "execution-badge pending";
    } finally {
        setLoading(false);
    }
});

// ── Ticket Actions ──────────────────────────────────────────────────────────

DOM.btnCopyId.addEventListener("click", () => {
    if (lastTicketId) {
        navigator.clipboard.writeText(lastTicketId).then(() => {
            DOM.btnCopyId.textContent = "✓ Copied!";
            setTimeout(() => { DOM.btnCopyId.textContent = "📋 Copy ID"; }, 2000);
        }).catch(() => {
            // Fallback for older browsers
            const temp = document.createElement("input");
            temp.value = lastTicketId;
            document.body.appendChild(temp);
            temp.select();
            document.execCommand("copy");
            document.body.removeChild(temp);
            DOM.btnCopyId.textContent = "✓ Copied!";
            setTimeout(() => { DOM.btnCopyId.textContent = "📋 Copy ID"; }, 2000);
        });
    }
});

DOM.btnTrackTicket.addEventListener("click", () => {
    if (lastTicketId) {
        DOM.trackInput.value = lastTicketId;
        navigateTo("track");
        trackTicket(lastTicketId);
    }
});

// ── Ticket Tracking ─────────────────────────────────────────────────────────

async function trackTicket(ticketId) {
    DOM.trackEmpty.classList.add("d-none");
    DOM.trackResult.classList.remove("d-none");
    DOM.trackResult.innerHTML = '<div style="text-align:center; padding:2rem; color:var(--on-surface-variant);">Loading...</div>';

    try {
        const res = await fetch("/status/track", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ticket_id: ticketId }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            DOM.trackResult.innerHTML = `
                <div class="card" style="text-align:center; padding:2rem;">
                    <div style="font-size:2rem; margin-bottom:1rem;">❌</div>
                    <h3 style="font-family:var(--font-display); margin-bottom:0.5rem;">Ticket Not Found</h3>
                    <p style="font-size:0.88rem; color:var(--on-surface-variant);">${err.detail || "Please check the ID and try again."}</p>
                </div>`;
            return;
        }

        const data = await res.json();
        renderTicketStatus(data.ticket);
        announce(`Ticket ${ticketId} status: ${data.ticket.status}`);

    } catch (err) {
        DOM.trackResult.innerHTML = `
            <div class="card" style="text-align:center; padding:2rem;">
                <div style="font-size:2rem; margin-bottom:1rem;">⚠️</div>
                <h3 style="font-family:var(--font-display); margin-bottom:0.5rem;">Connection Error</h3>
                <p style="font-size:0.88rem; color:var(--on-surface-variant);">${err.message}</p>
            </div>`;
    }
}

function renderTicketStatus(ticket) {
    const statusColors = {
        logged: "var(--status-info)",
        assigned: "var(--secondary)",
        in_progress: "var(--status-warning)",
        resolved: "var(--tertiary)",
        escalated: "var(--status-error)",
    };

    const statusLabels = {
        logged: "AI Logged",
        assigned: "Assigned",
        in_progress: "In Progress • QRT Dispatched",
        resolved: "Resolved",
        escalated: "Escalated",
    };

    let timelineHtml = '<div class="timeline">';
    if (ticket.timeline) {
        for (const step of ticket.timeline) {
            const dotClass = step.status === "completed" ? "completed" : step.status === "in_progress" ? "in-progress" : "pending";
            const icon = step.status === "completed" ? "✓" : step.status === "in_progress" ? "●" : step.step;
            timelineHtml += `
                <div class="timeline-step">
                    <div class="timeline-dot ${dotClass}">${icon}</div>
                    <div class="timeline-content">
                        <div class="timeline-title">${step.title}</div>
                        <div class="timeline-desc">${step.description}</div>
                        ${step.timestamp ? `<div class="timeline-time">${new Date(step.timestamp).toLocaleString("en-IN")}</div>` : ""}
                    </div>
                </div>`;
        }
    }
    timelineHtml += "</div>";

    DOM.trackResult.innerHTML = `
        <div class="card fade-in" style="margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
                <div>
                    <div style="font-family:var(--font-mono); font-size:0.78rem; color:var(--secondary); font-weight:600;">${ticket.ticket_id}</div>
                    <div style="display:flex; gap:0.5rem; align-items:center; margin:0.25rem 0;">
                        <span style="font-size:0.72rem; padding:0.2rem 0.55rem; background:var(--surface-dim); border-radius:var(--radius-full); color:var(--on-surface-variant);">${ticket.zone_name}</span>
                        <span style="font-size:0.72rem; padding:0.2rem 0.55rem; background:var(--surface-dim); border-radius:var(--radius-full); color:var(--on-surface-variant);">Ward ${ticket.ward_id}</span>
                    </div>
                    <h3 style="font-family:var(--font-display); font-size:1.25rem; font-weight:700; margin:0.5rem 0;">${ticket.area_or_address}</h3>
                    <span style="display:inline-flex; align-items:center; gap:0.35rem; padding:0.3rem 0.7rem; border-radius:var(--radius-full); font-size:0.78rem; font-weight:600; background:${statusColors[ticket.status] || "var(--surface-dim)"}; color:white;">
                        ● ${statusLabels[ticket.status] || ticket.status}
                    </span>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.78rem; color:var(--on-surface-variant);">Reported</div>
                    <div style="font-size:0.88rem; font-weight:600;">${new Date(ticket.created_at).toLocaleString("en-IN")}</div>
                    <div style="font-size:0.78rem; color:var(--on-surface-variant); margin-top:0.5rem;">Deadline</div>
                    <div style="font-size:0.88rem; font-weight:600; color:var(--secondary);">${new Date(ticket.resolution_eta).toLocaleString("en-IN")}</div>
                </div>
            </div>

            <div style="margin-top:1.5rem; padding-top:1rem; border-top:1px solid var(--outline-variant);">
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:1rem;">
                    <div>
                        <div style="font-size:0.72rem; color:var(--on-surface-variant);">Department</div>
                        <div style="font-size:0.88rem; font-weight:600;">${ticket.department_name}</div>
                    </div>
                    <div>
                        <div style="font-size:0.72rem; color:var(--on-surface-variant);">Severity</div>
                        <div style="font-size:0.88rem; font-weight:600; color:var(--secondary);">${ticket.severity_label} (Level ${ticket.severity}/5)</div>
                    </div>
                    <div>
                        <div style="font-size:0.72rem; color:var(--on-surface-variant);">SLA Clock</div>
                        <div style="font-size:0.88rem; font-weight:600;">${ticket.sla_hours} Hours</div>
                    </div>
                </div>
            </div>

            <div style="margin-top:1.5rem; padding-top:1rem; border-top:1px solid var(--outline-variant);">
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
                    <div>
                        <div style="font-size:0.72rem; color:var(--on-surface-variant);">Ward Officer</div>
                        <div style="font-size:0.88rem; font-weight:600;">${ticket.officer_name}</div>
                        <div style="font-size:0.78rem; color:var(--on-surface-variant);">${ticket.officer_phone}</div>
                    </div>
                    <div>
                        <div style="font-size:0.72rem; color:var(--on-surface-variant);">Citizen</div>
                        <div style="font-size:0.88rem; font-weight:600;">${ticket.citizen_name}</div>
                        <div style="font-size:0.78rem; color:var(--on-surface-variant);">${ticket.phone}</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card fade-in">
            <h3 style="font-family:var(--font-display); font-weight:600; margin-bottom:1rem;">Verification & Dispatch Timeline</h3>
            ${timelineHtml}
        </div>
    `;
}

DOM.btnTrack.addEventListener("click", () => {
    const id = DOM.trackInput.value.trim();
    if (id) trackTicket(id);
});

DOM.trackInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        const id = DOM.trackInput.value.trim();
        if (id) trackTicket(id);
    }
});

// ── Directory Page ──────────────────────────────────────────────────────────

async function loadDirectory() {
    try {
        const [wardsRes, deptsRes] = await Promise.all([
            fetch("/directory/wards"),
            fetch("/directory/departments"),
        ]);

        const wardsData = await wardsRes.json();
        const deptsData = await deptsRes.json();

        // Render wards
        if (wardsData.wards && DOM.wardGrid) {
            DOM.wardGrid.innerHTML = wardsData.wards.map((w) => `
                <div class="card ward-card">
                    <div class="ward-header">
                        <span class="ward-id">${w.ward_id} • PINCODE ${w.pincode}</span>
                        <span class="zone-badge">${w.zone_name}</span>
                    </div>
                    <h3>${w.ward_name}</h3>
                    <div class="officer-info">
                        <div>👤 ${w.officer_name} — ${w.officer_designation}</div>
                        <div>📞 ${w.officer_phone}</div>
                    </div>
                    <div class="landmarks">
                        <strong>Major Landmarks:</strong> ${w.landmarks.join(", ")}
                    </div>
                    <button class="btn btn-primary" style="margin-top:1rem; font-size:0.82rem;" onclick="quickFile('${w.ward_name}')">
                        📝 File Grievance in ${w.ward_name}
                    </button>
                </div>
            `).join("");
        }

        // Render departments
        const deptIcons = {
            "Roads & Buildings": "🛤",
            "Water & Sewerage": "🚰",
            "Solid Waste & Health": "🗑",
            "Streetlight & Electrical": "💡",
        };

        if (deptsData.departments && DOM.deptGrid) {
            DOM.deptGrid.innerHTML = deptsData.departments.map((d) => `
                <div class="card dept-card">
                    <div class="dept-icon">${deptIcons[d.department_name] || "🏛"}</div>
                    <h3>${d.department_name}</h3>
                    <div style="font-size:0.82rem; color:var(--on-surface-variant);">${d.division}</div>
                    <div style="font-size:0.82rem; margin-top:0.5rem;">
                        <strong>Nodal Officer:</strong> ${d.nodal_officer}
                    </div>
                    <div style="font-size:0.82rem;">
                        <strong>Helpline:</strong> <a href="tel:${d.helpline}" style="color:var(--secondary); font-weight:600;">${d.helpline}</a>
                    </div>
                    <div class="sla-info">
                        ⏱ Citizen Charter SLA: ${d.sla_hours} Hours
                    </div>
                </div>
            `).join("");
        }

        if (wardsData.total_wards) {
            const statW = document.getElementById("stat-wards");
            if (statW) statW.textContent = wardsData.total_wards;
        }
        if (deptsData.total_departments) {
            const statD = document.getElementById("stat-depts");
            if (statD) statD.textContent = deptsData.total_departments;
        }

    } catch (err) {
        console.error("Failed to load directory:", err);
    }
}

// Quick file from directory
window.quickFile = function(wardName) {
    DOM.areaAddress.value = wardName;
    navigateTo("report");
};

// ── Chat Widget ─────────────────────────────────────────────────────────────

const CHAT_RESPONSES = {
    status: "To check your complaint status, go to the **Ticket Lookup & Tracker** page and enter your AMC tracking ID (e.g. AMC-2025-RD-00001). You'll see real-time updates including SLA clock, assigned department, and dispatch timeline.",
    report: "To report a civic issue: 1) Go to **Report Issue** page, 2) Upload a photo or select a scenario, 3) Fill in your name, phone, and area, 4) Click Submit. The AI will auto-classify, assign ward, and generate your tracking ID!",
    sla: "AMC Citizen Charter SLA times:\n• **Roads & Buildings**: 48 hours\n• **Water & Sewerage**: 24 hours (6h for pipe bursts)\n• **Solid Waste & Health**: 12 hours\n• **Streetlight & Electrical**: 24 hours\n\nIf unresolved within SLA, automatic escalation to Deputy Municipal Commissioner.",
    ward: "Bodakdev (Ward W08) falls under **North West Zone**. Ward Officer: **R. V. Patel** (Junior Engineer, Roads). Contact: 079-26871201. Major landmarks: SG Highway, Sindhu Bhavan Road, Pakwan Crossroads, Judges Bungalow.",
    default: "I can help you with:\n• 📝 Filing a new civic complaint\n• 🔍 Checking ticket status\n• 🏛 Ward & department information\n• ⏱ SLA timelines\n\nPlease ask your question or use the quick action buttons above!",
};

function getChatResponse(message) {
    const lower = message.toLowerCase();
    if (lower.includes("status") || lower.includes("track") || lower.includes("check")) return CHAT_RESPONSES.status;
    if (lower.includes("report") || lower.includes("file") || lower.includes("complaint") || lower.includes("pothole")) return CHAT_RESPONSES.report;
    if (lower.includes("sla") || lower.includes("time") || lower.includes("how long") || lower.includes("deadline")) return CHAT_RESPONSES.sla;
    if (lower.includes("ward") || lower.includes("officer") || lower.includes("bodakdev") || lower.includes("department")) return CHAT_RESPONSES.ward;
    return CHAT_RESPONSES.default;
}

function addChatMessage(text, isUser) {
    const msg = document.createElement("div");
    msg.className = `chat-msg ${isUser ? "user" : "ai"}`;
    msg.textContent = text;
    DOM.chatFeed.appendChild(msg);
    DOM.chatFeed.scrollTop = DOM.chatFeed.scrollHeight;
}

DOM.chatToggle.addEventListener("click", () => {
    const isOpen = DOM.chatWidget.classList.toggle("open");
    DOM.chatToggle.setAttribute("aria-expanded", isOpen);
    if (isOpen) DOM.chatInput.focus();
});

DOM.chatClose.addEventListener("click", () => {
    DOM.chatWidget.classList.remove("open");
    DOM.chatToggle.setAttribute("aria-expanded", "false");
});

DOM.chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const msg = DOM.chatInput.value.trim();
    if (!msg) return;

    addChatMessage(msg, true);
    DOM.chatInput.value = "";

    setTimeout(() => {
        addChatMessage(getChatResponse(msg), false);
    }, 500);
});

DOM.chatChips.forEach((chip) => {
    chip.addEventListener("click", () => {
        const query = chip.dataset.query;
        if (query) {
            addChatMessage(query, true);
            setTimeout(() => {
                addChatMessage(getChatResponse(query), false);
            }, 500);
        }
    });
});

// ── Initialize ──────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
    // Load the first scenario by default
    const firstChip = document.querySelector(".scenario-chip.active");
    if (firstChip) firstChip.click();

    // Pre-load directory data
    loadDirectory();
});
