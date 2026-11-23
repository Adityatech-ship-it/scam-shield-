/**
 * Trust Who - Live Scam Radar & Heatmap
 * Visualizes anonymous community scam reports on an interactive map
 * with heat clusters, city markers, filters, and live incident feed.
 */

let radarMap = null;
let heatLayer = null;
let markersLayerGroup = null;
let allHeatPoints = [];

document.addEventListener("DOMContentLoaded", () => {
    initMap();
    loadHeatmapData();
    initFilters();
});

function initMap() {
    const mapElement = document.getElementById("map");
    if (!mapElement) return;

    // Centered on India with high zoom capability
    radarMap = L.map("map", {
        center: [21.5000, 78.9629],
        zoom: 5,
        minZoom: 4,
        maxZoom: 18,
        scrollWheelZoom: true
    });

    // Dark cyber map tile layer (CartoDB Dark Matter)
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: "abcd",
        maxZoom: 19
    }).addTo(radarMap);

    markersLayerGroup = L.layerGroup().addTo(radarMap);
    window.radarMap = radarMap;
}

async function loadHeatmapData(cityFilter = "", categoryFilter = "") {
    try {
        const res = await fetch("/api/heatmap");
        const data = await res.json();
        allHeatPoints = data.points || [];

        renderMapLayers(cityFilter, categoryFilter);
        loadLiveFeed(cityFilter, categoryFilter);
    } catch (err) {
        console.error("Failed to load heatmap data:", err);
    }
}

function renderMapLayers(cityFilter = "", categoryFilter = "") {
    if (!radarMap) return;

    // Filter points
    let filteredPoints = allHeatPoints;
    if (cityFilter) {
        filteredPoints = filteredPoints.filter(p => p.city.toLowerCase().includes(cityFilter.toLowerCase()));
    }
    if (categoryFilter) {
        filteredPoints = filteredPoints.filter(p => p.scam_type.toLowerCase().includes(categoryFilter.toLowerCase()));
    }

    // 1. Update Heat Layer
    if (heatLayer) {
        radarMap.removeLayer(heatLayer);
    }

    const heatCoords = filteredPoints.map(p => [p.lat, p.lon, p.intensity || 0.8]);
    if (typeof L.heatLayer === "function") {
        heatLayer = L.heatLayer(heatCoords, {
            radius: 28,
            blur: 20,
            maxZoom: 13,
            gradient: {
                0.2: "#3b82f6",
                0.5: "#eab308",
                0.8: "#f97316",
                1.0: "#ef4444"
            }
        }).addTo(radarMap);
    }

    // 2. Update Interactive Markers
    markersLayerGroup.clearLayers();

    filteredPoints.forEach(p => {
        // Custom neon circular marker
        const marker = L.circleMarker([p.lat, p.lon], {
            radius: 8,
            fillColor: "#ef4444",
            color: "#ffffff",
            weight: 1.5,
            opacity: 0.9,
            fillOpacity: 0.85
        });

        const popupContent = `
            <div class="p-1 space-y-1.5 text-xs">
                <div class="flex items-center justify-between border-b border-slate-700 pb-1">
                    <span class="font-bold text-slate-100 flex items-center">
                        <span class="w-2 h-2 rounded-full bg-red-500 mr-1.5"></span>
                        ${p.city}
                    </span>
                    <span class="text-[10px] text-slate-400">${p.time.split(" ")[0]}</span>
                </div>
                <div class="text-amber-400 font-semibold">${p.scam_type}</div>
                <div class="text-slate-300 italic bg-slate-900/80 p-1.5 rounded border border-slate-800">
                    "${p.snippet}"
                </div>
                <div class="text-[10px] text-red-400 font-medium">⚠️ Flagged by Anonymous Citizen</div>
            </div>
        `;

        marker.bindPopup(popupContent);
        markersLayerGroup.addLayer(marker);
    });

    // If filtered by city, auto-pan and zoom to the first matching point
    if (cityFilter && filteredPoints.length > 0) {
        radarMap.flyTo([filteredPoints[0].lat, filteredPoints[0].lon], 11, {
            duration: 1.2
        });
    }
}

async function loadLiveFeed(cityFilter = "", categoryFilter = "") {
    const feedContainer = document.getElementById("recent-reports-feed");
    if (!feedContainer) return;

    try {
        let url = `/api/reports?limit=25`;
        if (cityFilter) url += `&city=${encodeURIComponent(cityFilter)}`;
        if (categoryFilter) url += `&scam_type=${encodeURIComponent(categoryFilter)}`;

        const res = await fetch(url);
        const reports = await res.json();

        feedContainer.innerHTML = "";
        if (reports.length === 0) {
            feedContainer.innerHTML = `<div class="p-4 text-center text-xs text-slate-500">No reports found matching criteria.</div>`;
            return;
        }

        reports.forEach(r => {
            const item = document.createElement("div");
            item.className = "p-3 rounded-lg bg-slate-800/60 border border-slate-700/50 hover:border-slate-600 transition-all cursor-pointer";
            item.innerHTML = `
                <div class="flex items-center justify-between mb-1">
                    <span class="font-semibold text-xs text-blue-400">${r.city}</span>
                    <span class="text-[10px] text-slate-400">${r.created_at}</span>
                </div>
                <div class="text-xs font-medium text-slate-200 mb-1">${r.scam_type}</div>
                <p class="text-xs text-slate-400 line-clamp-2 italic">"${r.message_snippet}"</p>
                ${r.suspect_identifier ? `<div class="mt-1 text-[10px] text-red-400 font-mono">Reported handle: ${r.suspect_identifier}</div>` : ''}
            `;

            // Clicking feed card zooms to marker on map
            item.addEventListener("click", () => {
                if (radarMap) {
                    radarMap.flyTo([r.lat, r.lon], 12, { duration: 1 });
                }
            });

            feedContainer.appendChild(item);
        });
    } catch (err) {
        console.error("Failed to load reports feed:", err);
    }
}

function initFilters() {
    const citySelect = document.getElementById("filter-city");
    const categorySelect = document.getElementById("filter-category");
    const resetBtn = document.getElementById("btn-reset-filters");

    function applyFilters() {
        const city = citySelect ? citySelect.value : "";
        const cat = categorySelect ? categorySelect.value : "";
        renderMapLayers(city, cat);
        loadLiveFeed(city, cat);
    }

    if (citySelect) citySelect.addEventListener("change", applyFilters);
    if (categorySelect) categorySelect.addEventListener("change", applyFilters);

    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            if (citySelect) citySelect.value = "";
            if (categorySelect) categorySelect.value = "";
            renderMapLayers("", "");
            loadLiveFeed("", "");
            if (radarMap) {
                radarMap.flyTo([21.5000, 78.9629], 5, { duration: 1 });
            }
        });
    }
}

// Global refresh callback
window.refreshRadarMap = function() {
    loadHeatmapData();
};
