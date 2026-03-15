
/**
 * PhotoIntel — map.js
 * --------------------
 * Handles all integration between the forensic report data and the
 * CesiumJS 3D globe (MapView).
 *
 * Responsible for:
 *   - Transforming API profiles into MapView-compatible point objects
 *   - Rendering the collection overview panel in the map sidebar
 *   - Rendering the per-image detail panel when a globe point is clicked
 *
 * Dependencies:
 *   - MapView object   from map_view.js
 *   - sanitizeHTML()   from app.js
 *   - formatDate()     from app.js
 *   - window.currentReportData set by initializeMapData()
 *
 * Sections:
 *   1. Map Initialization
 *   2. Sidebar — Collection Overview
 *   3. Sidebar — Point Detail
 */


// ─────────────────────────────────────────
// 1. Map Initialization
// ─────────────────────────────────────────

/**
 * Stores the full API report for cross-screen access.
 * Set here so both map.js and ui.js can reference the same data.
 * @type {Object|null}
 */
window.currentReportData = null;

/**
 * Prepares geospatial data from the API report and initializes the MapView.
 *
 * Filters profiles to those with valid GPS coordinates, maps them to the
 * format expected by MapView.renderPoints(), and passes device switch events
 * for trajectory line rendering.
 *
 * @param {Object} reportData - Full CollectionInsights object from the API.
 */
function initializeMapData(reportData) {
    window.currentReportData = reportData;

    if (typeof MapView === 'undefined') {
        console.warn('MapView not found. Skipping map initialization.');
        return;
    }

    const mapPoints = reportData.image_profiles
        .filter(p => p.latitude && p.longitude)
        .map(p => ({
            name:         p.filename,
            lat:          p.latitude,
            lng:          p.longitude,
            device:       p.device || 'Unknown Device',
            timestamp:    p.timestamp || 'N/A',
            is_suspicious: p.is_suspicious,
            issues: {
                ai:       p.ai_issue,
                gps:      p.gps_issue,
                software: p.software_issue,
                temporal: p.temporal_issue,
                optical:  p.optical_issue,
                altitude: p.altitude_issue,
                device:   p.device_issue
            }
        }));

    MapView.init('cesium-container', updateMapOverlay);
    MapView.renderPoints(mapPoints, reportData.device_timeline_switches);
    renderMapOverview();
}


// ─────────────────────────────────────────
// 2. Sidebar — Collection Overview
// ─────────────────────────────────────────

/**
 * Renders the collection-level statistics panel in the map sidebar.
 *
 * Displayed when no point is selected. Shows total files, suspicious count,
 * geotagged count, date range, device switches, and anomaly breakdown.
 * Suspicious files count is highlighted in pale pink when non-zero.
 */
window.renderMapOverview = function() {
    const data = window.currentReportData;
    const contentEl = document.getElementById('overlay-content');
    if (!contentEl || !data) return;

    const PALE_PINK   = '#ffccd5';
    const switchCount = (data.device_timeline_switches || []).length;

    // Warning triangle icon — shown only when suspicious files exist
    const warningIcon = data.suspicious_images > 0
        ? `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
               style="margin-right:8px;">
               <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
               <line x1="12" y1="9"  x2="12"   y2="13"/>
               <line x1="12" y1="17" x2="12.01" y2="17"/>
           </svg>`
        : '';

    contentEl.innerHTML = `
        <div style="font-size:10px;text-transform:uppercase;letter-spacing:2px;
                    color:rgba(255,255,255,0.4);margin-bottom:32px;">
            Collection Insights
        </div>

        <div class="stat-box">
            <h4>Total Files Analyzed</h4>
            <div class="val">${data.total_count}</div>
        </div>

        <div class="stat-box">
            <h4>Suspicious Files</h4>
            <div class="val" style="display:flex;align-items:center;
                font-weight:${data.suspicious_images > 0 ? '600' : '300'};
                color:${data.suspicious_images > 0 ? PALE_PINK : '#fff'};
                opacity:${data.suspicious_images > 0 ? '1' : '0.4'};">
                ${warningIcon}${data.suspicious_images}
            </div>
        </div>

        <div class="stat-box">
            <h4>Geotagged Files</h4>
            <div class="val">${data.images_with_gps}</div>
        </div>

        <div class="stat-box">
            <h4>Date Range</h4>
            <div style="font-size:13px;font-weight:300;color:rgba(255,255,255,0.8);
                        margin-top:4px;line-height:1.8;">
                <span style="color:rgba(255,255,255,0.4);font-size:11px;">From</span><br>
                <span style="font-weight:400;color:#fff;">${formatDate(data.start_date)}</span><br>
                <span style="color:rgba(255,255,255,0.4);font-size:11px;">To</span><br>
                <span style="font-weight:400;color:#fff;">${formatDate(data.end_date)}</span>
            </div>
        </div>

        <div class="stat-box">
            <h4>Device Switches</h4>
            <div class="val" style="color:#fff;opacity:${switchCount > 0 ? '1' : '0.4'};">
                ${switchCount}
            </div>
        </div>

        <div class="stat-box" style="border-bottom:none;">
            <h4>Anomaly Breakdown</h4>
            <div style="font-size:13px;font-weight:300;color:rgba(255,255,255,0.6);
                        margin-top:8px;line-height:1.8;">
                AI Generated:    <span style="font-weight:600;color:#fff;">${data.ai_count}</span><br>
                Software Edited: <span style="font-weight:600;color:#fff;">${data.software_edit_count}</span><br>
                GPS Tampering:   <span style="font-weight:600;color:#fff;">${data.gps_tampering_count}</span><br>
                Device Anomaly:  <span style="font-weight:600;color:#fff;">${data.device_anomaly_count}</span>
            </div>
        </div>

        <div style="margin-top:40px;font-size:10px;color:rgba(255,255,255,0.3);
                    letter-spacing:1px;text-transform:uppercase;
                    border-top:1px solid rgba(255,255,255,0.08);padding-top:16px;">
            Select a data point on the map to view specific forensics
        </div>
    `;
};


// ─────────────────────────────────────────
// 3. Sidebar — Point Detail
// ─────────────────────────────────────────

/**
 * Renders the per-image forensic detail panel in the map sidebar.
 *
 * Called by MapView when the user clicks a point on the globe.
 * Displays the image's filename, device, timestamp, and a list of all
 * triggered forensic rule violations. A "Back to Overview" button
 * restores the collection panel.
 *
 * @param {Object} data - Point data object passed from MapView on click.
 * @param {string}  data.name         - Image filename.
 * @param {string}  data.device       - Device model string.
 * @param {string}  data.timestamp    - Capture timestamp string.
 * @param {boolean} data.is_suspicious - Whether any forensic flag was triggered.
 * @param {Object}  data.issues       - Map of rule keys to boolean flag values.
 */
function updateMapOverlay(data) {
    const contentEl = document.getElementById('overlay-content');
    if (!contentEl) return;

    const PALE_PINK = '#ffccd5';

    const warningSvg = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        style="margin-right:6px;vertical-align:text-bottom;">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9"  x2="12"   y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>`;

    const safeSvg = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        style="margin-right:6px;vertical-align:text-bottom;">
        <polyline points="20 6 9 17 4 12"/>
    </svg>`;

    const statusText   = data.is_suspicious ? 'STATUS: SUSPICIOUS ANOMALY' : 'STATUS: LOGICALLY CONSISTENT';
    const statusIcon   = data.is_suspicious ? warningSvg : safeSvg;
    const statusColor  = data.is_suspicious ? PALE_PINK  : 'rgba(255,255,255,0.4)';
    const statusWeight = data.is_suspicious ? '600'      : '400';

    // Human-readable labels for each forensic rule key
    const issueLabels = {
        ai:       'AI Generation Detected',
        gps:      'GPS Tampering Suspected',
        software: 'Edited via External Software',
        temporal: 'Time-Location Inconsistency',
        optical:  'Optical Data Mismatch',
        altitude: 'Implausible GPS Altitude',
        device:   'Virtual/Emulator Device Signature',
    };

    const issuesHtml = data.is_suspicious
        ? `<ul style="list-style-type:square;color:${PALE_PINK};font-size:13px;
                      padding-left:16px;margin-top:12px;line-height:1.8;font-weight:400;">
               ${Object.entries(issueLabels)
                   .filter(([key]) => data.issues?.[key])
                   .map(([, label]) => `
                       <li>
                           <span style="color:rgba(255,255,255,0.8);font-weight:300;">
                               ${label}
                           </span>
                       </li>`)
                   .join('')}
           </ul>`
        : `<div style="color:rgba(255,255,255,0.4);font-size:13px;margin-top:12px;
                       font-weight:300;font-style:italic;">
               No forensic anomalies detected.
           </div>`;

    contentEl.innerHTML = `
        <button onclick="renderMapOverview()"
                style="background:none;border:none;color:rgba(255,255,255,0.5);
                       cursor:pointer;font-size:10px;text-transform:uppercase;
                       letter-spacing:1px;margin-bottom:32px;padding:0;
                       font-family:inherit;transition:color 0.2s;"
                onmouseover="this.style.color='#fff'"
                onmouseout="this.style.color='rgba(255,255,255,0.5)'">
            ← BACK TO OVERVIEW
        </button>

        <div style="display:flex;align-items:center;color:${statusColor};
                    font-weight:${statusWeight};font-size:11px;letter-spacing:1.5px;
                    text-transform:uppercase;border-bottom:1px solid rgba(255,255,255,0.08);
                    padding-bottom:12px;margin-bottom:24px;">
            ${statusIcon}${statusText}
        </div>

        <div style="font-size:13px;font-weight:300;color:rgba(255,255,255,0.7);line-height:2;">
            <div style="display:flex;flex-direction:column;margin-bottom:16px;">
                <span style="font-size:10px;text-transform:uppercase;letter-spacing:1px;
                             color:rgba(255,255,255,0.4);">File Name</span>
                <span style="font-weight:400;color:#fff;word-break:break-all;">
                    ${sanitizeHTML(data.name)}
                </span>
            </div>
            <div style="display:flex;flex-direction:column;margin-bottom:16px;">
                <span style="font-size:10px;text-transform:uppercase;letter-spacing:1px;
                             color:rgba(255,255,255,0.4);">Device Signature</span>
                <span style="font-weight:400;color:#fff;">${sanitizeHTML(data.device)}</span>
            </div>
            <div style="display:flex;flex-direction:column;margin-bottom:24px;">
                <span style="font-size:10px;text-transform:uppercase;letter-spacing:1px;
                             color:rgba(255,255,255,0.4);">Timestamp</span>
                <span style="font-weight:400;color:#fff;">${sanitizeHTML(data.timestamp)}</span>
            </div>
        </div>

        <div style="background:rgba(255,255,255,0.03);padding:16px;border-radius:8px;
                    border:1px solid rgba(255,255,255,0.05);">
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:1.5px;
                        color:rgba(255,255,255,0.5);">Risk Report</div>
            ${issuesHtml}
        </div>
    `;
}
