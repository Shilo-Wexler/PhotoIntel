
/**
 * PhotoIntel — app.js
 * --------------------
 * Core single-page application controller.
 *
 * Handles the application lifecycle: screen navigation, modal management,
 * file upload processing, drag-and-drop setup, and DOM initialization.
 * Utility functions used across ui.js and map.js are also defined here.
 *
 * Dependencies:
 *   - ui.js       must be loaded before app.js
 *   - map.js      must be loaded before app.js
 *   - map_view.js must be loaded before app.js
 *
 * Sections:
 *   1. Utilities
 *   2. Navigation
 *   3. Modal
 *   4. File Processing & API
 *   5. Drag & Drop
 *   6. Initialization
 */


// ─────────────────────────────────────────
// 1. Utilities
// ─────────────────────────────────────────

/**
 * Escapes user-supplied strings before injecting into innerHTML.
 * Prevents XSS by encoding all HTML special characters.
 *
 * @param {string} str - Raw input string (e.g. filename from API).
 * @returns {string} HTML-safe string safe for use in innerHTML.
 */
function sanitizeHTML(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Formats an ISO date string into a short human-readable date.
 *
 * @param {string|null} dateStr - ISO 8601 date string or null.
 * @returns {string} Formatted date (e.g. "18 Jan 2023") or "N/A" if invalid.
 */
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    if (isNaN(d)) return 'N/A';
    return d.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}


// ─────────────────────────────────────────
// 2. Navigation
// ─────────────────────────────────────────

/**
 * Switches the visible screen in the SPA.
 *
 * Removes the 'active' class from all screens, then adds it to the target.
 * Also manages the 'map-active' body class (which hides the nav bar on the
 * map screen) and re-initializes Lucide icons after each transition.
 *
 * @param {string} screenId - The DOM id of the screen element to show.
 */
window.showScreen = function(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });

    // Close any open modal on navigation
    document.getElementById('analysis-modal')?.classList.remove('active');

    const targetScreen = document.getElementById(screenId);
    if (targetScreen) {
        targetScreen.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Toggle full-screen map mode (hides navigation bar)
        document.body.classList.toggle('map-active', screenId === 'screen-map');

        // Re-render Lucide icons injected by renderImageList / report nav
        if (typeof lucide !== 'undefined') lucide.createIcons();
    } else {
        console.error(`Navigation Error: Screen '${screenId}' not found.`);
    }
};


// ─────────────────────────────────────────
// 3. Modal
// ─────────────────────────────────────────

/**
 * Opens the analysis type selection modal.
 * Triggered by the "Start Investigation" CTA button on the landing page.
 */
window.openAnalysisModal = function() {
    document.getElementById('analysis-modal').classList.add('active');
};

/**
 * Closes the modal when the user clicks the backdrop area.
 * Clicking inside the modal content does not close it.
 *
 * @param {MouseEvent} e - The click event on the overlay element.
 */
window.closeAnalysisModal = function(e) {
    if (e.target.id === 'analysis-modal') {
        document.getElementById('analysis-modal').classList.remove('active');
    }
};


// ─────────────────────────────────────────
// 4. File Processing & API
// ─────────────────────────────────────────

/**
 * Submits a FileList to the FastAPI /analyze endpoint and renders results.
 *
 * Shows the loading screen during the request. On success, renders the
 * stats strip, image list, and initializes map data, then navigates to
 * the Audit Summary screen. On failure, shows an alert and returns to
 * the landing screen.
 *
 * @param {FileList} files - Files from a file input or drag-and-drop event.
 */
async function processFiles(files) {
    if (!files || files.length === 0) return;

    showScreen('screen-loading');

    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorDetail = await response.json();
            throw new Error(errorDetail.detail || 'Server error');
        }

        const reportData = await response.json();

        // Render all report components (defined in ui.js and map.js)
        renderStatsStrip(reportData);
        renderImageList(reportData.image_profiles || []);
        initializeMapData(reportData);

        showScreen('screen-report-list');

    } catch (error) {
        console.error('Analysis failed:', error);
        alert('Analysis error: ' + error.message);
        showScreen('screen-landing');
    }
}


// ─────────────────────────────────────────
// 5. Drag & Drop
// ─────────────────────────────────────────

/**
 * Attaches all file input and drag-and-drop event listeners to a dropzone.
 *
 * Handles three input methods:
 *   - Click on the dropzone area → triggers the hidden file input
 *   - File input change event → processes selected files
 *   - Drag-and-drop → processes dropped files
 *
 * @param {string} dropzoneId - ID of the dropzone container element.
 * @param {string} inputId    - ID of the hidden <input type="file"> element.
 */
function setupDropzone(dropzoneId, inputId) {
    const dropzone = document.getElementById(dropzoneId);
    const input    = document.getElementById(inputId);
    if (!dropzone || !input) return;

    // Click anywhere on dropzone to open file picker
    dropzone.addEventListener('click', () => input.click());

    // Process files after selection via file picker
    input.addEventListener('change', (e) => {
        processFiles(e.target.files);
        e.target.value = ''; // Reset so the same file can be re-selected
    });

    // Visual feedback during drag
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('drag-over');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('drag-over');
    });

    // Process dropped files
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('drag-over');
        processFiles(e.dataTransfer.files);
    });
}


// ─────────────────────────────────────────
// 6. Initialization
// ─────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {

    // Wire up both upload dropzones
    setupDropzone('dropzone-single', 'input-single');
    setupDropzone('dropzone-folder', 'input-folder');

    // Initialize Lucide icons on first load
    if (typeof lucide !== 'undefined') lucide.createIcons();

    // ── Stats Strip: mouse wheel horizontal scroll ──────────────────────────
    document.addEventListener('wheel', (e) => {
        const strip = document.getElementById('stats-strip');
        if (strip?.matches(':hover')) {
            e.preventDefault();
            strip.scrollLeft += e.deltaY;
        }
    }, { passive: false });

    // ── Stats Strip: drag-to-scroll ─────────────────────────────────────────
    let isDragging  = false;
    let startX      = 0;
    let scrollStart = 0;

    document.addEventListener('mousedown', (e) => {
        const strip = document.getElementById('stats-strip');
        if (strip?.matches(':hover')) {
            isDragging  = true;
            startX      = e.clientX;
            scrollStart = strip.scrollLeft;
            strip.style.cursor = 'grabbing';
        }
    });

    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const strip = document.getElementById('stats-strip');
        if (strip) strip.scrollLeft = scrollStart - (e.clientX - startX);
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        const strip = document.getElementById('stats-strip');
        if (strip) strip.style.cursor = 'grab';
    });

});

window.askAI = async function(index) {
    const profiles = window.currentReportData?.image_profiles;
    if (!profiles?.[index]) return;

    const input = document.getElementById('ai-question-input');
    const answer = document.getElementById('ai-answer');
    const btn = document.getElementById('ai-ask-btn');

    const question = input?.value?.trim();
    if (!question) return;

    btn.disabled = true;
    answer.textContent = 'Analyzing...';

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question,
                profile: profiles[index]
            })
        });

        const data = await response.json();
        answer.textContent = data.answer || 'No response received.';

    } catch (err) {
        answer.textContent = 'Error contacting AI assistant.';
        console.error(err);
    } finally {
        btn.disabled = false;
    }
};