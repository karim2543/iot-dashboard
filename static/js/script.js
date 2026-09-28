/**
 * NEXUS IoT — Analytiques & Graphiques
 * ENET'Com Sfax
 */

let tempChartInstance     = null;
let humidityChartInstance = null;
let barLineChartInstance  = null;
let radarChartInstance    = null;

// ─── Palette Light professionnelle ────────────────────────
const C = {
    cyan:       '#2563eb',
    cyanAlpha:  'rgba(37, 99, 235, 0.08)',
    amber:      '#ea580c',
    amberAlpha: 'rgba(234, 88, 12, 0.10)',
    red:        '#dc2626',
    redAlpha:   'rgba(220, 38, 38, 0.08)',
    green:      '#16a34a',
    greenAlpha: 'rgba(22, 163, 74, 0.10)',
    purple:     '#7c3aed',
    purpleAlpha:'rgba(124, 58, 237, 0.10)',
    grid:       'rgba(15, 23, 42, 0.05)',
    tick:       '#94a3b8',
    legend:     '#64748b',
    font:       'DM Sans',
};

// ─── Options communes ──────────────────────────────────────
const baseScales = {
    y: {
        grid:  { color: C.grid, drawBorder: false },
        ticks: { color: C.tick, font: { family: C.font, size: 10 } },
        border: { dash: [4, 4] }
    },
    x: {
        grid:  { display: false },
        ticks: { color: C.tick, font: { family: C.font, size: 10 } }
    }
};

const commonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                color: C.legend,
                font: { family: C.font, size: 10 },
                boxWidth: 12,
                padding: 16
            }
        }
    },
    scales: baseScales
};

// ─── Horloge ──────────────────────────────────────────────
function updateClock() {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');

    const clockEl = document.getElementById('real-clock');
    if (clockEl) clockEl.textContent =
        `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;

    const dateEl = document.getElementById('real-date');
    if (dateEl) dateEl.textContent = now.toLocaleDateString('fr-FR', {
        day: 'numeric', month: 'long', year: 'numeric'
    });
}

// ─── Rafraîchissement graphiques ──────────────────────────
async function refreshAnalyticsCharts() {
    try {
        const response = await fetch('/api/analytics');
        if (!response.ok) throw new Error('API /api/analytics — erreur ' + response.status);
        const data = await response.json();

        // 1. Températures (ligne)
        const tempCtx = document.getElementById('tempChart');
        if (tempCtx) {
            if (!tempChartInstance) {
                tempChartInstance = new Chart(tempCtx, {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [
                            {
                                label: 'Extérieur (°C)',
                                data: data.temp_ext_log,
                                borderColor: C.cyan,
                                backgroundColor: C.cyanAlpha,
                                fill: true,
                                borderWidth: 2,
                                pointRadius: 2,
                                pointBackgroundColor: C.cyan,
                                tension: 0.4
                            },
                            {
                                label: 'Intérieur Labo (°C)',
                                data: data.temp_int_log,
                                borderColor: C.amber,
                                backgroundColor: C.amberAlpha,
                                fill: true,
                                borderWidth: 2,
                                pointRadius: 2,
                                pointBackgroundColor: C.amber,
                                tension: 0.4
                            }
                        ]
                    },
                    options: commonChartOptions
                });
            } else {
                tempChartInstance.data.labels = data.labels;
                tempChartInstance.data.datasets[0].data = data.temp_ext_log;
                tempChartInstance.data.datasets[1].data = data.temp_int_log;
                tempChartInstance.update();
            }
        }

        // 2. Humidité (barres)
        const humCtx = document.getElementById('humidityChart');
        if (humCtx) {
            if (!humidityChartInstance) {
                humidityChartInstance = new Chart(humCtx, {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Humidité (%)',
                            data: data.humidity_log,
                            backgroundColor: C.cyanAlpha,
                            borderColor: C.cyan,
                            borderWidth: 1,
                            borderRadius: 4,
                            barPercentage: 0.5
                        }]
                    },
                    options: commonChartOptions
                });
            } else {
                humidityChartInstance.data.labels = data.labels;
                humidityChartInstance.data.datasets[0].data = data.humidity_log;
                humidityChartInstance.update();
            }
        }

        // 3. Pression (ligne) + Vent (barre) — axes doubles
        const barLineCtx = document.getElementById('barLineChart');
        if (barLineCtx) {
            if (!barLineChartInstance) {
                barLineChartInstance = new Chart(barLineCtx, {
                    data: {
                        labels: data.labels,
                        datasets: [
                            {
                                type: 'line',
                                label: 'Pression (hPa)',
                                data: data.pressure_log,
                                borderColor: C.red,
                                backgroundColor: 'transparent',
                                borderWidth: 2,
                                pointRadius: 2,
                                pointBackgroundColor: C.red,
                                tension: 0.4,
                                yAxisID: 'y'
                            },
                            {
                                type: 'bar',
                                label: 'Vent (m/s)',
                                data: data.wind_log,
                                backgroundColor: C.greenAlpha,
                                borderColor: C.green,
                                borderWidth: 1,
                                borderRadius: 4,
                                barPercentage: 0.45,
                                yAxisID: 'y1'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: { color: C.legend, font: { family: C.font, size: 10 }, boxWidth: 12, padding: 16 }
                            }
                        },
                        scales: {
                            x: {
                                grid: { display: false },
                                ticks: { color: C.tick, font: { family: C.font, size: 10 } }
                            },
                            y: {
                                position: 'left',
                                grid: { color: C.grid, drawBorder: false },
                                ticks: { color: C.red, font: { family: C.font, size: 10 } }
                            },
                            y1: {
                                position: 'right',
                                grid: { display: false },
                                ticks: { color: C.green, font: { family: C.font, size: 10 } }
                            }
                        }
                    }
                });
            } else {
                barLineChartInstance.data.labels = data.labels;
                barLineChartInstance.data.datasets[0].data = data.pressure_log;
                barLineChartInstance.data.datasets[1].data = data.wind_log;
                barLineChartInstance.update();
            }
        }

        // 4. Radar AQI
        const radarCtx = document.getElementById('radarChart');
        if (radarCtx) {
            if (!radarChartInstance) {
                radarChartInstance = new Chart(radarCtx, {
                    type: 'radar',
                    data: {
                        labels: ['PM2.5', 'PM10', 'CO2', 'NO2', 'O3'],
                        datasets: [{
                            label: 'Concentration (ppm)',
                            data: data.radar_aqi,
                            backgroundColor: C.purpleAlpha,
                            borderColor: C.purple,
                            borderWidth: 2,
                            pointBackgroundColor: C.purple,
                            pointRadius: 3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                labels: { color: C.legend, font: { family: C.font, size: 10 }, boxWidth: 12 }
                            }
                        },
                        scales: {
                            r: {
                                angleLines: { color: 'rgba(0, 200, 255, 0.1)' },
                                grid:        { color: 'rgba(0, 200, 255, 0.08)' },
                                pointLabels: { color: C.legend, font: { family: C.font, size: 9 } },
                                ticks:       { display: false }
                            }
                        }
                    }
                });
            } else {
                radarChartInstance.data.datasets[0].data = data.radar_aqi;
                radarChartInstance.update();
            }
        }

    } catch (err) {
        console.error('[NEXUS] Erreur rafraîchissement graphiques :', err);
    }
}

// ─── Init ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {

    // Horloge
    updateClock();
    setInterval(updateClock, 1000);

    // Graphiques (init + polling 10s)
    refreshAnalyticsCharts();
    setInterval(refreshAnalyticsCharts, 10000);

    // Gear button toggle
    const gearButton = document.getElementById('gearButton');
    if (gearButton) {
        gearButton.addEventListener('click', () => {
            gearButton.classList.toggle('active');
        });
    }
});