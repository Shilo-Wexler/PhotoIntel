
/**
 * PhotoIntel — ui.js
 * ------------------
 * Responsible for all dynamic UI rendering in the report screens.
 *
 * This module bridges the raw API response data and the DOM,
 * transforming ImageRiskProfile objects into interactive HTML components.
 *
 * Dependencies:
 *   - sanitizeHTML()  from app.js
 *   - formatDate()    from app.js
 *   - showScreen()    from app.js
 *
 * Sections:
 *   1. Stats Strip
 *   2. Image List
 *   3. Image Detail
 */


// ─────────────────────────────────────────
// 1. Stats Strip
// ─────────────────────────────────────────

/**
 * Renders the horizontally scrollable statistics strip above the image list.
 *
 * Each metric is displayed as a frosted-glass card. Cards representing
 * non-zero anomaly counts are highlighted with a red alert style.
 *
 * @param {Object} data - The full CollectionInsights object from the API.
 */
function renderStatsStrip(data) {
    const strip = document.getElementById('stats-strip');
    if (!strip || !data) return;

    const cards = [
        { label: 'Total Files',     value: data.total_count },
        { label: 'Suspicious',      value: data.suspicious_images,                          alert: data.suspicious_images > 0 },
        { label: 'Geotagged',       value: data.images_with_gps },
        { label: 'With EXIF',       value: data.images_with_exif },
        { label: 'AI Generated',    value: data.ai_count,                                   alert: data.ai_count > 0 },
        { label: 'Software Edited', value: data.software_edit_count,                        alert: data.software_edit_count > 0 },
        { label: 'GPS Tampering',   value: data.gps_tampering_count,                        alert: data.gps_tampering_count > 0 },
        { label: 'Device Anomaly',  value: data.device_anomaly_count,                       alert: data.device_anomaly_count > 0 },
        { label: 'Device Switches', value: (data.device_timeline_switches || []).length },
        { label: 'Teleportation',   value: (data.teleportation_incidents || []).length,     alert: (data.teleportation_incidents || []).length > 0 },
        { label: 'Clusters',        value: (data.location_clusters || []).length },
        { label: 'Start Date',      value: formatDate(data.start_date), small: true },
        { label: 'End Date',        value: formatDate(data.end_date),   small: true },
    ];

    strip.innerHTML = cards.map(card => `
        <div class="stat-card ${card.alert ? 'stat-card-alert' : ''}">
            <div class="stat-card-label">${card.label}</div>
            <div class="stat-card-value ${card.small ? 'stat-card-value-small' : ''}">
                ${card.value}
            </div>
        </div>
    `).join('');
}


// ─────────────────────────────────────────
// 2. Image List
// ─────────────────────────────────────────

/**
 * Renders the scrollable list of analyzed images in the Audit Summary screen.
 *
 * Profiles are sorted chronologically (newest first), with undated items
 * placed at the bottom. Each row is clickable and navigates to the detail screen.
 * Suspicious items receive a red left border and a red index circle.
 *
 * @param {Array<ImageRiskProfile>} profiles - Array of image risk profiles from the API.
 */
function renderImageList(profiles) {
    const list = document.getElementById('image-list');
    if (!list) return;

    // Sort by timestamp descending; profiles without timestamps go to the end
    const sorted = [...profiles].sort((a, b) => {
        if (!a.timestamp && !b.timestamp) return 0;
        if (!a.timestamp) return 1;
        if (!b.timestamp) return -1;
        return new Date(b.timestamp) - new Date(a.timestamp);
    });

    list.innerHTML = sorted.map((profile, index) => {
        const isRisk = profile.is_suspicious;
        const safeFilename = sanitizeHTML(profile.filename || 'Unknown');
        const safeDevice   = sanitizeHTML(profile.device   || 'Unknown Device');
        const timestamp    = profile.timestamp
            ? new Date(profile.timestamp).toLocaleDateString('en-GB', {
                day: '2-digit', month: 'short', year: 'numeric'
              })
            : 'N/A';

        return `
            <div class="image-list-item ${isRisk ? 'image-list-item-risk' : ''}"
                 onclick="showImageDetail(${index})">
                <div class="image-list-index">${index + 1}</div>
                <div class="image-list-info">
                    <div class="image-list-filename">${safeFilename}</div>
                    <div class="image-list-meta">${safeDevice} · ${timestamp}</div>
                </div>
                <div class="image-list-badge ${isRisk ? 'badge-risk' : 'badge-clean'}">
                    ${isRisk ? 'High Risk' : 'Clean'}
                </div>
                <div class="image-list-arrow">›</div>
            </div>
        `;
    }).join('');
}


// ─────────────────────────────────────────
// 3. Image Detail
// ─────────────────────────────────────────

/**
 * Renders the full forensic detail view for a single image and navigates to it.
 *
 * Displays all available metadata fields alongside a checklist of all seven
 * forensic rule results. Triggered flags are shown in red with a warning icon;
 * passed rules are shown in muted gray with a checkmark.
 *
 * @param {number} index - Index into currentReportData.image_profiles (sorted order).
 */
window.showImageDetail = function(index) {
    const profiles = window.currentReportData?.image_profiles;
    if (!profiles?.[index]) return;

    const p = profiles[index];
    const contentEl = document.getElementById('image-detail-content');
    if (!contentEl) return;

    const flags = [
        { label: 'AI Generated',          value: p.ai_issue },
        { label: 'GPS Tampering',          value: p.gps_issue },
        { label: 'Software Edited',        value: p.software_issue },
        { label: 'Temporal Inconsistency', value: p.temporal_issue },
        { label: 'Optical Mismatch',       value: p.optical_issue },
        { label: 'Altitude Anomaly',       value: p.altitude_issue },
        { label: 'Virtual Device',         value: p.device_issue },
    ];

    contentEl.innerHTML = `
        <div class="detail-card">
            <div class="detail-status ${p.is_suspicious ? 'detail-status-risk' : 'detail-status-clean'}">
                ${p.is_suspicious ? '🔴 Suspicious Anomaly Detected' : '🟢 Logically Consistent'}
            </div>

            <div class="detail-grid">
                <div class="detail-field">
                    <div class="detail-field-label">Filename</div>
                    <div class="detail-field-value">${sanitizeHTML(p.filename || 'Unknown')}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Device</div>
                    <div class="detail-field-value">${sanitizeHTML(p.device || 'Unknown Device')}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Timestamp</div>
                    <div class="detail-field-value">
                        ${p.timestamp ? new Date(p.timestamp).toLocaleString('en-GB') : 'N/A'}
                    </div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">Coordinates</div>
                    <div class="detail-field-value">${p.latitude ?? 'N/A'}, ${p.longitude ?? 'N/A'}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-field-label">EXIF Data</div>
                    <div class="detail-field-value">${p.has_exif ? 'Present' : 'Missing'}</div>
                </div>
            </div>

            <div class="detail-flags-title">Forensic Flags</div>
            <div class="detail-flags">
                ${flags.map(f => `
                    <div class="detail-flag ${f.value ? 'detail-flag-triggered' : 'detail-flag-clear'}">
                        <span class="detail-flag-icon">${f.value ? '⚠️' : '✓'}</span>
                        <span>${f.label}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    showScreen('screen-image-detail');
};