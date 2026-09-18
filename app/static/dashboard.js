const API_KEY = "agizleme-staj-2026-gizli-anahtar-x7f2k9";  // .env'deki key ile AYNI olmalı
const REFRESH_INTERVAL_MS = 30000; // 30 saniye

const headers = {
    "X-API-Key": API_KEY
};

let allDevices = [];       // filtreleme için ham cihaz verisini saklıyoruz
let severityChart = null;  // grafik nesnelerini saklıyoruz ki her yenilemede yok edip yeniden çizebilelim
let eventsChart = null;

async function loadDashboard() {
    try {
        await Promise.all([
            loadDevices(),
            loadAlerts(),
            loadEvents()
        ]);
        document.getElementById("last-updated").textContent =
            "Son güncelleme: " + new Date().toLocaleTimeString("tr-TR");
    } catch (error) {
        console.error("Dashboard yüklenirken hata:", error);
        document.getElementById("last-updated").textContent = "Hata: veri yüklenemedi";
    }
}

async function loadDevices() {
    const response = await fetch("/devices/", { headers });
    const devices = await response.json();

    allDevices = devices; // ham veriyi sakla, filtreleme bunun üzerinden çalışacak

    const total = devices.length;
    const online = devices.filter(d => d.status === "online").length;
    const offline = devices.filter(d => d.status === "offline").length;

    document.getElementById("stat-total-devices").textContent = total;
    document.getElementById("stat-online").textContent = online;
    document.getElementById("stat-offline").textContent = offline;

    renderDeviceTable();
}

function renderDeviceTable() {
    const searchTerm = document.getElementById("device-search").value.toLowerCase();
    const statusFilter = document.getElementById("device-status-filter").value;

    let filtered = allDevices.filter(device => {
        const matchesSearch =
            device.name.toLowerCase().includes(searchTerm) ||
            device.ip_address.toLowerCase().includes(searchTerm);
        const matchesStatus =
            statusFilter === "all" || device.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const tbody = document.getElementById("devices-tbody");
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">Eşleşen cihaz bulunamadı</td></tr>';
        return;
    }

    tbody.innerHTML = filtered.map(device => `
        <tr>
            <td>${device.name}</td>
            <td>${device.ip_address}</td>
            <td>${device.device_type || "-"}</td>
            <td><span class="status-badge status-${device.status}">${device.status}</span></td>
        </tr>
    `).join("");
}

async function loadAlerts() {
    const response = await fetch("/alerts/", { headers });
    const allAlerts = await response.json();
    const openAlerts = allAlerts.filter(a => !a.is_resolved);

    document.getElementById("stat-open-alerts").textContent = openAlerts.length;

    const tbody = document.getElementById("alerts-tbody");
    if (openAlerts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">Açık uyarı yok</td></tr>';
    } else {
        tbody.innerHTML = openAlerts.map(alert => `
            <tr>
                <td>${alert.device_id}</td>
                <td><span class="severity-${alert.severity}">${alert.severity}</span></td>
                <td>${alert.message}</td>
                <td>${new Date(alert.created_at).toLocaleString("tr-TR")}</td>
            </tr>
        `).join("");
    }

    renderSeverityChart(allAlerts);
}

async function loadEvents() {
    const response = await fetch("/events/", { headers });
    const events = await response.json();

    const recentEvents = events.slice(0, 10);

    const tbody = document.getElementById("events-tbody");
    if (recentEvents.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">Henüz olay yok</td></tr>';
    } else {
        tbody.innerHTML = recentEvents.map(event => `
            <tr>
                <td>${event.source_ip}</td>
                <td>${event.event_type}</td>
                <td><span class="severity-${event.severity}">${event.severity}</span></td>
                <td>${event.description || "-"}</td>
                <td>${new Date(event.timestamp).toLocaleString("tr-TR")}</td>
            </tr>
        `).join("");
    }

    renderEventsChart(events);
}

function renderSeverityChart(alerts) {
    const counts = {};
    alerts.forEach(alert => {
        counts[alert.severity] = (counts[alert.severity] || 0) + 1;
    });

    const labels = Object.keys(counts);
    const data = Object.values(counts);
    const colorMap = { warning: "#f59e0b", critical: "#dc2626" };
    const colors = labels.map(l => colorMap[l] || "#94a3b8");

    const ctx = document.getElementById("severity-chart");

    if (severityChart) {
        severityChart.destroy(); // önceki grafiği temizle, üst üste binmesin
    }

    if (labels.length === 0) {
        return; // hiç alert yoksa grafik çizmeye gerek yok
    }

    severityChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

function renderEventsChart(events) {
    // Son 24 saati saatlik dilimlere böl
    const now = new Date();
    const hourBuckets = Array(24).fill(0);
    const hourLabels = [];

    for (let i = 23; i >= 0; i--) {
        const hour = new Date(now - i * 60 * 60 * 1000);
        hourLabels.push(hour.getHours() + ":00");
    }

    events.forEach(event => {
        const eventTime = new Date(event.timestamp);
        const hoursAgo = Math.floor((now - eventTime) / (60 * 60 * 1000));
        if (hoursAgo >= 0 && hoursAgo < 24) {
            hourBuckets[23 - hoursAgo]++;
        }
    });

    const ctx = document.getElementById("events-chart");

    if (eventsChart) {
        eventsChart.destroy();
    }

    eventsChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: hourLabels,
            datasets: [{
                label: "Olay Sayısı",
                data: hourBuckets,
                backgroundColor: "#2563eb"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, ticks: { stepSize: 1 } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Sayfa ilk açıldığında yükle
loadDashboard();

// Elle yenile butonu
document.getElementById("refresh-btn").addEventListener("click", loadDashboard);

// Otomatik yenileme (30 saniyede bir)
setInterval(loadDashboard, REFRESH_INTERVAL_MS);

// Arama ve filtre değiştiğinde tabloyu anında güncelle (backend'e yeni istek atmadan)
document.getElementById("device-search").addEventListener("input", renderDeviceTable);
document.getElementById("device-status-filter").addEventListener("change", renderDeviceTable);
// --- Karanlık / Aydınlık Mod ---
function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const btn = document.getElementById("theme-toggle-btn");
    btn.textContent = theme === "dark" ? "☀️ Aydınlık Mod" : "🌙 Karanlık Mod";
    localStorage.setItem("dashboard-theme", theme);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
}

// Sayfa açıldığında, daha önce seçilmiş bir tema varsa onu uygula
const savedTheme = localStorage.getItem("dashboard-theme") || "light";
applyTheme(savedTheme);

document.getElementById("theme-toggle-btn").addEventListener("click", toggleTheme);