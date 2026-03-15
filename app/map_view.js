

/**
 * PhotoIntel — map_view.js
 * -------------------------
 * CesiumJS 3D globe wrapper for forensic geospatial visualization.
 *
 * Encapsulates all direct interactions with the Cesium Viewer:
 * initialization, camera control, click handling, and entity rendering.
 * Designed as a stateless-from-outside interface — callers only need
 * init(), renderPoints(), and destroy().
 *
 * Dependencies:
 *   - CesiumJS (loaded via CDN in index.html)
 *   - CONFIG.CESIUM_TOKEN (from config.js)
 *   - window.renderMapOverview() (from map.js) — called on empty-click
 *
 * Sections:
 *   1. Initialization
 *   2. Camera
 *   3. Interactivity
 *   4. Rendering
 *   5. Cleanup
 */

const MapView = {

    /** @type {Cesium.Viewer|null} Active CesiumJS viewer instance. */
    viewer: null,

    /** @type {Function|null} Callback invoked when a map point is clicked. */
    onPointClickCallback: null,


    // ─────────────────────────────────────────
    // 1. Initialization
    // ─────────────────────────────────────────

    /**
     * Creates and configures the CesiumJS Viewer inside the given container.
     *
     * Guards against double-initialization. After mounting, shows a radar
     * loading overlay that fades out once the globe tiles have fully loaded.
     *
     * @param {string}   containerId  - ID of the DOM element to mount the viewer into.
     * @param {Function} onPointClick - Callback receiving point data on entity click.
     */
    init: function(containerId, onPointClick) {
        if (this.viewer) return;

        this.onPointClickCallback = onPointClick;
        Cesium.Ion.defaultAccessToken = CONFIG.CESIUM_TOKEN;

        this.viewer = new Cesium.Viewer(containerId, {
            terrain:              Cesium.Terrain.fromWorldTerrain(),
            baseLayer:            Cesium.ImageryLayer.fromProviderAsync(
                                      Cesium.IonImageryProvider.fromAssetId(3)
                                  ),
            animation:            false,
            timeline:             false,
            baseLayerPicker:      false,
            navigationHelpButton: false,
            geocoder:             false,
            homeButton:           false,
            sceneModePicker:      false,
            infoBox:              false,
            selectionIndicator:   false,
            requestRenderMode:    true,
            maximumRenderTimeChange: Infinity
        });

        // Hide Cesium branding
        if (this.viewer.cesiumWidget.creditContainer) {
            this.viewer.cesiumWidget.creditContainer.style.display = 'none';
        }

        // Camera zoom constraints
        this.viewer.scene.screenSpaceCameraController.minimumZoomDistance = 500;
        this.viewer.scene.screenSpaceCameraController.maximumZoomDistance = 25000000;

        this.resetView();
        this.viewer.scene.requestRender();
        this._showLoadingOverlay(containerId);
        this.setupInteractivity();
    },

    /**
     * Creates and mounts the radar-style loading overlay.
     * The overlay fades out automatically once all globe tiles are loaded.
     *
     * @private
     * @param {string} containerId - ID of the container to append the overlay to.
     */
    _showLoadingOverlay: function(containerId) {
        const overlay = document.createElement('div');
        overlay.id = 'cesium-loading';

        overlay.innerHTML = `
            <svg width="160" height="160" viewBox="0 0 160 160">
                <circle cx="80" cy="80" r="70" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
                <circle cx="80" cy="80" r="50" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
                <circle cx="80" cy="80" r="30" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
                <line x1="80"  y1="10" x2="80"  y2="80" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
                <line x1="150" y1="80" x2="10"  y2="80" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
                <defs>
                    <radialGradient id="sweep" cx="80" cy="80" r="70" gradientUnits="userSpaceOnUse">
                        <stop offset="0%"   stop-color="rgba(255,255,255,0.0)"/>
                        <stop offset="100%" stop-color="rgba(255,255,255,0.25)"/>
                    </radialGradient>
                </defs>
                <path d="M80,80 L80,10 A70,70 0 0,1 150,80 Z" fill="url(#sweep)" opacity="0.5">
                    <animateTransform attributeName="transform" type="rotate"
                        from="0 80 80" to="360 80 80" dur="2.5s" repeatCount="indefinite"/>
                </path>
                <line x1="80" y1="80" x2="80" y2="10" stroke="rgba(255,255,255,0.9)" stroke-width="1.5">
                    <animateTransform attributeName="transform" type="rotate"
                        from="0 80 80" to="360 80 80" dur="2.5s" repeatCount="indefinite"/>
                </line>
                <circle cx="80" cy="80" r="3" fill="rgba(255,255,255,0.8)"/>
            </svg>
            <div style="margin-top:20px;font-size:11px;letter-spacing:3px;
                        color:rgba(255,255,255,0.4);text-transform:uppercase;">
                Initializing Globe
            </div>
        `;

        overlay.style.cssText = `
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: #000;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 999;
            transition: opacity 0.8s ease;
        `;

        document.getElementById(containerId).appendChild(overlay);

        // Fade out and remove once all tiles have loaded
        const unsubscribe = this.viewer.scene.globe.tileLoadProgressEvent
            .addEventListener((remaining) => {
                if (remaining === 0) {
                    overlay.style.opacity = '0';
                    setTimeout(() => overlay.remove(), 800);
                    unsubscribe();
                }
            });
    },


    // ─────────────────────────────────────────
    // 2. Camera
    // ─────────────────────────────────────────

    /**
     * Smoothly flies the camera to the default overview position.
     *
     * Centered over Israel at an altitude that shows the full region.
     * Pitch is set to -90° (top-down) so the globe appears centered.
     */
    resetView: function() {
        if (!this.viewer) return;

        this.viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(34.81, 32.08, 12000000.0),
            orientation: {
                heading: 0.0,
                pitch:   Cesium.Math.toRadians(-90.0),
                roll:    0.0
            },
            duration: 1.5
        });

        this.viewer.scene.requestRender();
    },


    // ─────────────────────────────────────────
    // 3. Interactivity
    // ─────────────────────────────────────────

    /**
     * Registers left-click handlers on the globe canvas.
     *
     * Clicking a point entity:
     *   - Flies the camera to it at a 45° oblique angle
     *   - Extracts the attached originalData property
     *   - Invokes onPointClickCallback with the point data
     *
     * Clicking an empty area:
     *   - Resets the camera to the overview position
     *   - Calls window.renderMapOverview() to restore the sidebar
     *
     * Polyline entities (timeline/device-switch lines) are ignored on click.
     */
    setupInteractivity: function() {
        const handler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);
        let isFlying = false;

        handler.setInputAction((click) => {
            if (isFlying) return;

            const pickedObject = this.viewer.scene.pick(click.position);

            if (Cesium.defined(pickedObject) && pickedObject.id) {
                const entity = pickedObject.id;

                // Ignore polyline entities (timeline and device-switch lines)
                if (entity.polyline) return;

                isFlying = true;

                this.viewer.flyTo(entity, {
                    duration: 1.5,
                    offset: new Cesium.HeadingPitchRange(
                        0,
                        Cesium.Math.toRadians(-45),
                        80000
                    )
                })
                .then(()  => { isFlying = false; })
                .catch(() => { isFlying = false; });

                const data = entity.properties?.originalData?.getValue?.();
                if (this.onPointClickCallback && data) {
                    this.onPointClickCallback(data);
                }

            } else {
                // Empty click — return to overview
                this.resetView();
                if (window.renderMapOverview) window.renderMapOverview();
            }

        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    },


    // ─────────────────────────────────────────
    // 4. Rendering
    // ─────────────────────────────────────────

    /**
     * Renders all forensic data points and trajectory lines onto the globe.
     *
     * Draws three layers in order:
     *   1. Cyan timeline polylines connecting consecutive geotagged images
     *   2. Pink device-switch polylines connecting points where the device changed
     *   3. Colored point entities (cyan = clean, pink = suspicious)
     *
     * After rendering, resets the camera to the top-down overview.
     *
     * @param {Array<Object>} locations      - Geotagged image profiles with lat/lng.
     * @param {Array<Object>} deviceSwitches - Device transition events with coord pairs.
     */
    renderPoints: function(locations, deviceSwitches) {
        if (!this.viewer || !Array.isArray(locations)) return;

        this.viewer.entities.removeAll();

        const validPoints = locations.filter(
            p => typeof p.lat === 'number' && typeof p.lng === 'number'
        );

        // Layer 1: Timeline polylines (cyan, thin)
        for (let i = 0; i < validPoints.length - 1; i++) {
            const curr = validPoints[i];
            const next = validPoints[i + 1];

            this.viewer.entities.add({
                polyline: {
                    positions: Cesium.Cartesian3.fromDegreesArray([
                        curr.lng, curr.lat,
                        next.lng, next.lat
                    ]),
                    width: 1.5,
                    material: new Cesium.PolylineGlowMaterialProperty({
                        glowPower: 0.1,
                        color: Cesium.Color.fromCssColorString('#00f2ff').withAlpha(0.4)
                    }),
                    clampToGround: false
                }
            });
        }

        // Layer 2: Device-switch polylines (pink, thicker)
        if (Array.isArray(deviceSwitches)) {
            deviceSwitches.forEach((sw) => {
                if (!sw.coords || sw.coords.length < 2) return;
                const [from, to] = sw.coords;

                this.viewer.entities.add({
                    polyline: {
                        positions: Cesium.Cartesian3.fromDegreesArray([
                            from[1], from[0],
                            to[1],   to[0]
                        ]),
                        width: 2.5,
                        material: new Cesium.PolylineGlowMaterialProperty({
                            glowPower: 0.2,
                            color: Cesium.Color.fromCssColorString('#ffccd5').withAlpha(0.8)
                        }),
                        clampToGround: false
                    }
                });
            });
        }

        // Layer 3: Point entities
        validPoints.forEach((point) => {
            const color = point.is_suspicious
                ? Cesium.Color.fromCssColorString('#ffccd5')  // Pale pink — suspicious
                : Cesium.Color.fromCssColorString('#00f2ff'); // Cyan — clean

            this.viewer.entities.add({
                position: Cesium.Cartesian3.fromDegrees(point.lng, point.lat),
                point: {
                    pixelSize:                12,
                    color:                    color,
                    outlineColor:             Cesium.Color.WHITE.withAlpha(0.6),
                    outlineWidth:             2,
                    disableDepthTestDistance: Number.POSITIVE_INFINITY
                },
                properties: { originalData: point }
            });
        });

        // Reset camera to top-down overview after rendering
        this.viewer.camera.setView({
            destination: Cesium.Cartesian3.fromDegrees(34.81, 32.08, 12000000.0),
            orientation: {
                heading: 0.0,
                pitch:   Cesium.Math.toRadians(-90.0),
                roll:    0.0
            }
        });

        this.viewer.scene.requestRender();
    },


    // ─────────────────────────────────────────
    // 5. Cleanup
    // ─────────────────────────────────────────

    /**
     * Destroys the CesiumJS viewer and releases all GPU/memory resources.
     * Should be called when navigating away from the map screen in an SPA.
     */
    destroy: function() {
        if (this.viewer) {
            this.viewer.destroy();
            this.viewer = null;
        }
        this.onPointClickCallback = null;
    }

};


