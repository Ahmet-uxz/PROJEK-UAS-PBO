document.addEventListener("DOMContentLoaded", function () {
  const mapContainer = document.getElementById("tps-map");
  if (!mapContainer) return; // halaman tanpa hasil pencarian → tidak ada peta

  let locations = [];
  try {
    locations = JSON.parse(mapContainer.dataset.locations || "[]");
  } catch (err) {
    console.error("Gagal membaca data lokasi TPS:", err);
    return;
  }

  if (!locations.length) return;

  // Hitung titik tengah (rata-rata koordinat) sebagai pusat peta awal
  const avgLat = locations.reduce((sum, loc) => sum + loc.latitude, 0) / locations.length;
  const avgLon = locations.reduce((sum, loc) => sum + loc.longitude, 0) / locations.length;

  const map = L.map("tps-map").setView([avgLat, avgLon], 13);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(map);

  const markerBounds = [];

  locations.forEach(function (loc, index) {
    const marker = L.marker([loc.latitude, loc.longitude]).addTo(map);

    const popupHtml =
      "<strong>" + (index + 1) + ". " + escapeHtml(loc.name) + "</strong><br>" +
      "<span style='font-size:.85em;color:#495057;'>" + escapeHtml(loc.address) + "</span><br>" +
      "<span style='font-size:.78em;color:#6c757d;'>" +
      loc.latitude.toFixed(6) + ", " + loc.longitude.toFixed(6) +
      "</span>";

    marker.bindPopup(popupHtml);
    markerBounds.push([loc.latitude, loc.longitude]);
  });

  // Sesuaikan zoom agar semua marker terlihat dalam satu frame
  if (markerBounds.length > 1) {
    map.fitBounds(markerBounds, { padding: [30, 30] });
  }

  // Klik baris tabel → buka popup marker terkait & pan ke lokasi
  document.querySelectorAll("[data-row-index]").forEach(function (row) {
    row.addEventListener("click", function () {
      const idx = parseInt(row.dataset.rowIndex, 10);
      const loc = locations[idx];
      if (!loc) return;
      map.setView([loc.latitude, loc.longitude], 16);
    });
  });

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
});
