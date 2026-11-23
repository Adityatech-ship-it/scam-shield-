/**
 * Trust  who - Core Frontend Logic
 * Manages Tab Navigation, Text & Screenshot OCR Detection,
 * Family Alerts, Preset Demonstrations, and Anonymous Reporting.
 */

// Global State
let currentAnalysisResult = null;

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    loadPresets();
    loadStats();
    initScreenshotOCR();
    initDetector();
    initReportForm();
});

// 1. Tab Navigation
function initTabs() {
    const tabButtons = document.querySelectorAll(".nav-tab-btn");
    const tabPanels = document.querySelectorAll(".tab-panel");

    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            tabButtons.forEach(b => {
                b.classList.remove("tab-active", "text-white");
                b.classList.add("text-slate-400");
            });
            btn.classList.add("tab-active", "text-white");
            btn.classList.remove("text-slate-400");

            tabPanels.forEach(panel => {
                if (panel.id === `tab-${targetTab}`) {
                    panel.classList.remove("hidden");
                } else {
                    panel.classList.add("hidden");
                }
            });

            // Trigger map resize if radar tab opened
            if (targetTab === "radar" && window.radarMap) {
                setTimeout(() => {
                    window.radarMap.invalidateSize();
                }, 100);
            }
        });
    });
}

// 2. Load Preset Scams for 1-Click Demo
async function loadPresets() {
    const container = document.getElementById("presets-container");
    if (!container) return;

    try {
        const res = await fetch("/api/presets");
        const presets = await res.json();

        container.innerHTML = "";
        presets.forEach(p => {
            const btn = document.createElement("button");
            btn.className = "text-left p-3 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 transition-all flex flex-col justify-between group";
            btn.innerHTML = `
                <div class="flex items-center justify-between w-full mb-1">
                    <span class="text-sm font-semibold text-slate-200 group-hover:text-blue-400 transition-colors">${p.title}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded ${p.badge === 'Legitimate' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'}">${p.badge}</span>
                </div>
                <p class="text-xs text-slate-400 line-clamp-2">${p.sample}</p>
            `;
            btn.addEventListener("click", () => {
                document.getElementById("message-input").value = p.sample;
                analyzeMessage(p.sample);
            });
            container.appendChild(btn);
        });
    } catch (err) {
        console.error("Failed to load presets:", err);
    }
}

// 3. Stats & Trending Alert Banner
async function loadStats() {
    try {
        const res = await fetch("/api/stats");
        const data = await res.json();

        const banner = document.getElementById("trending-banner-text");
        if (banner && data.trending) {
            banner.innerHTML = `<strong>${data.trending.scam_type}</strong> is currently trending near <strong>${data.trending.city}</strong> with ${data.trending.count} recent incident reports.`;
        }

        const totalCounter = document.getElementById("stat-total-reports");
        if (totalCounter) {
            totalCounter.textContent = data.total_reports || "0";
        }
    } catch (err) {
        console.error("Failed to load stats:", err);
    }
}

// 4. In-Browser OCR for Screenshots (Tesseract.js)
function initScreenshotOCR() {
    const dropzone = document.getElementById("screenshot-dropzone");
    const fileInput = document.getElementById("screenshot-file-input");
    const ocrStatus = document.getElementById("ocr-status");
    const ocrProgress = document.getElementById("ocr-progress-bar");
    const ocrText = document.getElementById("ocr-status-text");

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dropzone-active");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dropzone-active");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dropzone-active");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processScreenshot(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            processScreenshot(e.target.files[0]);
        }
    });

    async function processScreenshot(file) {
        if (!file.type.startsWith("image/")) {
            alert("Please upload an image file (PNG, JPG, WebP).");
            return;
        }

        ocrStatus.classList.remove("hidden");
        ocrText.textContent = "Extracting text from screenshot...";
        ocrProgress.style.width = "20%";

        try {
            if (typeof Tesseract === "undefined") {
                ocrText.textContent = "OCR engine initializing...";
            }

            const worker = await Tesseract.createWorker("eng");
            ocrProgress.style.width = "40%";

            const ret = await worker.recognize(file);
            ocrProgress.style.width = "90%";
            await worker.terminate();

            const extracted = ret.data.text.trim();
            ocrProgress.style.width = "100%";
            ocrText.textContent = "Text extracted successfully!";

            setTimeout(() => {
                ocrStatus.classList.add("hidden");
            }, 1200);

            if (extracted.length > 5) {
                document.getElementById("message-input").value = extracted;
                analyzeMessage(extracted);
            } else {
                alert("Could not clearly read text from the image. Please try pasting the message text directly.");
            }
        } catch (err) {
            console.error("OCR Error:", err);
            ocrText.textContent = "Error reading image. Please paste text directly.";
            setTimeout(() => {
                ocrStatus.classList.add("hidden");
            }, 2500);
        }
    }
}

// 5. Scam Detection Logic
function initDetector() {
    const analyzeBtn = document.getElementById("btn-analyze");
    const clearBtn = document.getElementById("btn-clear");
    const input = document.getElementById("message-input");

    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", () => {
            const text = input.value.trim();
            if (!text) {
                alert("Please enter or paste suspicious message text first.");
                return;
            }
            analyzeMessage(text);
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            input.value = "";
            document.getElementById("analysis-result-card").classList.add("hidden");
        });
    }

    // Copy Family Warning Button
    const copyWarnBtn = document.getElementById("btn-copy-warning");
    if (copyWarnBtn) {
        copyWarnBtn.addEventListener("click", () => {
            if (!currentAnalysisResult || !currentAnalysisResult.family_warning) return;
            navigator.clipboard.writeText(currentAnalysisResult.family_warning).then(() => {
                copyWarnBtn.innerHTML = `
                    <svg class="w-4 h-4 mr-1 text-emerald-400 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                    Copied Warning!
                `;
                setTimeout(() => {
                    copyWarnBtn.innerHTML = `
                        <svg class="w-4 h-4 mr-1 text-slate-300 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path></svg>
                        Copy Alert
                    `;
                }, 2000);
            });
        });
    }

    // Share via WhatsApp Button
    const whatsappBtn = document.getElementById("btn-whatsapp-warning");
    if (whatsappBtn) {
        whatsappBtn.addEventListener("click", () => {
            if (!currentAnalysisResult || !currentAnalysisResult.family_warning) return;
            const encoded = encodeURIComponent(currentAnalysisResult.family_warning);
            window.open(`https://wa.me/?text=${encoded}`, "_blank");
        });
    }

    // Quick Report Button from Result Card
    const reportFromAnalysisBtn = document.getElementById("btn-report-from-analysis");
    if (reportFromAnalysisBtn) {
        reportFromAnalysisBtn.addEventListener("click", () => {
            if (!currentAnalysisResult) return;
            
            // Switch to Report tab
            const reportNavBtn = document.querySelector('[data-tab="report"]');
            if (reportNavBtn) reportNavBtn.click();

            // Populate form
            document.getElementById("report-scam-type").value = currentAnalysisResult.category || "Suspicious Communication";
            document.getElementById("report-snippet").value = document.getElementById("message-input").value;
        });
    }
}

async function analyzeMessage(text) {
    const resultCard = document.getElementById("analysis-result-card");
    const loader = document.getElementById("analysis-loader");

    if (loader) loader.classList.remove("hidden");
    if (resultCard) resultCard.classList.add("hidden");

    try {
        const res = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });
        const data = await res.json();
        currentAnalysisResult = data;
        renderAnalysisResult(data);
    } catch (err) {
        console.error("Analysis request failed:", err);
        alert("Failed to connect to the analysis engine. Please verify the server is running.");
    } finally {
        if (loader) loader.classList.add("hidden");
    }
}

function renderAnalysisResult(data) {
    const card = document.getElementById("analysis-result-card");
    if (!card) return;

    card.classList.remove("hidden");

    // Verdict Badge & Colors
    const badge = document.getElementById("res-verdict-badge");
    const scoreText = document.getElementById("res-score-text");
    const scoreBar = document.getElementById("res-score-bar");
    const categoryText = document.getElementById("res-category");
    const explanationText = document.getElementById("res-explanation");
    const redFlagsList = document.getElementById("res-red-flags");
    const doList = document.getElementById("res-action-do");
    const dontList = document.getElementById("res-action-dont");
    const familyPreview = document.getElementById("res-family-preview");

    // Clear previous list items
    redFlagsList.innerHTML = "";
    doList.innerHTML = "";
    dontList.innerHTML = "";

    // Style according to risk level
    if (data.risk_level === "danger") {
        badge.className = "px-4 py-1.5 rounded-full text-sm font-bold bg-red-600/30 text-red-400 border border-red-500/50 badge-glow-red flex items-center";
        badge.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-red-500 mr-2 animate-ping"></span> ${data.verdict}`;
        scoreBar.className = "h-full bg-gradient-to-r from-orange-500 to-red-600 rounded-full transition-all duration-700";
    } else if (data.risk_level === "warning") {
        badge.className = "px-4 py-1.5 rounded-full text-sm font-bold bg-amber-500/30 text-amber-300 border border-amber-500/50 flex items-center";
        badge.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-amber-400 mr-2"></span> ${data.verdict}`;
        scoreBar.className = "h-full bg-amber-500 rounded-full transition-all duration-700";
    } else {
        badge.className = "px-4 py-1.5 rounded-full text-sm font-bold bg-emerald-600/30 text-emerald-400 border border-emerald-500/50 badge-glow-green flex items-center";
        badge.innerHTML = `<span class="w-2.5 h-2.5 rounded-full bg-emerald-400 mr-2"></span> ${data.verdict}`;
        scoreBar.className = "h-full bg-emerald-500 rounded-full transition-all duration-700";
    }

    scoreText.textContent = `${data.risk_score}% Risk`;
    scoreBar.style.width = `${data.risk_score}%`;
    categoryText.textContent = data.category;
    explanationText.textContent = data.explanation;

    // Render Red Flags
    if (data.red_flags && data.red_flags.length > 0) {
        data.red_flags.forEach(flag => {
            const li = document.createElement("li");
            li.className = "flex items-start text-xs text-red-300 bg-red-950/40 p-2 rounded border border-red-900/30";
            li.innerHTML = `
                <svg class="w-4 h-4 text-red-400 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                <span>${flag}</span>
            `;
            redFlagsList.appendChild(li);
        });
    } else {
        redFlagsList.innerHTML = `<p class="text-xs text-slate-400 italic">No glaring red flags identified.</p>`;
    }

    // Render Actions Do
    data.action_do.forEach(item => {
        const li = document.createElement("li");
        li.className = "flex items-start text-xs text-emerald-300";
        li.innerHTML = `
            <svg class="w-4 h-4 text-emerald-400 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
            <span>${item}</span>
        `;
        doList.appendChild(li);
    });

    // Render Actions Don't
    data.action_dont.forEach(item => {
        const li = document.createElement("li");
        li.className = "flex items-start text-xs text-rose-300 font-medium";
        li.innerHTML = `
            <svg class="w-4 h-4 text-rose-500 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            <span>${item}</span>
        `;
        dontList.appendChild(li);
    });

    // Family Warning Preview
    if (familyPreview) {
        familyPreview.textContent = data.family_warning;
    }

    // Smooth scroll down to result
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// 6. Anonymous Scam Reporting Form
function initReportForm() {
    const form = document.getElementById("anonymous-report-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const city = document.getElementById("report-city").value;
        const scamType = document.getElementById("report-scam-type").value;
        const snippet = document.getElementById("report-snippet").value;
        const suspect = document.getElementById("report-suspect").value;
        const pincode = document.getElementById("report-pincode").value;

        const submitBtn = document.getElementById("btn-submit-report");
        submitBtn.disabled = true;
        submitBtn.textContent = "Publishing anonymously...";

        try {
            const res = await fetch("/api/reports", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    city,
                    scam_type: scamType,
                    message_snippet: snippet,
                    suspect_identifier: suspect,
                    pincode
                })
            });
            const data = await res.json();
            if (data.success) {
                alert("Report logged anonymously! It has been pinned on the Live Scam Radar to protect others.");
                form.reset();
                loadStats();
                if (window.refreshRadarMap) {
                    window.refreshRadarMap();
                }
                // Switch to radar tab to see it live
                const radarNavBtn = document.querySelector('[data-tab="radar"]');
                if (radarNavBtn) radarNavBtn.click();
            } else {
                alert(data.error || "Failed to submit report.");
            }
        } catch (err) {
            console.error("Report submit error:", err);
            alert("Error sending report. Please check server.");
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Submit Anonymous Report";
        }
    });
}
