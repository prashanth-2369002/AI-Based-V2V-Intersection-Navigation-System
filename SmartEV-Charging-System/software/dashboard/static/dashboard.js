/* Smart EV Dashboard — frontend polling and chart logic */

const POLL_INTERVAL_MS = 5000;
const MAX_HISTORY_POINTS = 60;

// ─── Chart setup ─────────────────────────────────────────────────────────────

const chartDefaults = {
  responsive: true,
  animation: false,
  plugins: { legend: { labels: { color: '#d1d5db', font: { size: 11 } } } },
  scales: {
    x: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: '#374151' } },
    y: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { color: '#374151' } },
  },
};

const socChart = new Chart(document.getElementById('chart-soc'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'SOC (%)',   data: [], borderColor: '#4ade80', tension: 0.3, yAxisID: 'y', pointRadius: 0 },
      { label: 'Power (W)', data: [], borderColor: '#facc15', tension: 0.3, yAxisID: 'y1', pointRadius: 0 },
    ],
  },
  options: {
    ...chartDefaults,
    scales: {
      ...chartDefaults.scales,
      y:  { ...chartDefaults.scales.y, min: 0, max: 100, position: 'left' },
      y1: { ...chartDefaults.scales.y, position: 'right', grid: { drawOnChartArea: false } },
    },
  },
});

const tempChart = new Chart(document.getElementById('chart-temp'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'Temp (°C)',    data: [], borderColor: '#fb923c', tension: 0.3, yAxisID: 'y',  pointRadius: 0 },
      { label: 'Voltage (V)', data: [], borderColor: '#60a5fa', tension: 0.3, yAxisID: 'y1', pointRadius: 0 },
    ],
  },
  options: {
    ...chartDefaults,
    scales: {
      ...chartDefaults.scales,
      y:  { ...chartDefaults.scales.y, position: 'left' },
      y1: { ...chartDefaults.scales.y, position: 'right', grid: { drawOnChartArea: false } },
    },
  },
});

function pushToChart(chart, label, ...values) {
  chart.data.labels.push(label);
  values.forEach((v, i) => chart.data.datasets[i].data.push(v));
  if (chart.data.labels.length > MAX_HISTORY_POINTS) {
    chart.data.labels.shift();
    chart.data.datasets.forEach(ds => ds.data.shift());
  }
  chart.update();
}

// ─── Live data ────────────────────────────────────────────────────────────────

function formatElapsed(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
}

async function pollLive() {
  try {
    const res  = await fetch('/api/live');
    const data = await res.json();
    if (data.status === 'no_data') return;

    document.getElementById('val-soc').textContent     = `${data.soc.toFixed(1)}%`;
    document.getElementById('bar-soc').style.width     = `${Math.min(data.soc, 100)}%`;
    document.getElementById('val-voltage').textContent  = `${data.voltage.toFixed(2)}V`;
    document.getElementById('val-current').textContent  = data.current.toFixed(3);
    document.getElementById('val-power').textContent    = `${data.power_w.toFixed(1)}W`;
    document.getElementById('val-energy').textContent   = data.energy_wh.toFixed(2);
    document.getElementById('val-temp').textContent     = `${data.temp_c.toFixed(1)}°C`;
    document.getElementById('val-elapsed').textContent  = formatElapsed(data.elapsed_s);
    document.getElementById('last-update').textContent  = `Updated: ${new Date().toLocaleTimeString()}`;

    const t = new Date(data.timestamp).toLocaleTimeString();
    pushToChart(socChart, t, data.soc, data.power_w);
    pushToChart(tempChart, t, data.temp_c, data.voltage);
  } catch (e) {
    console.warn('Live poll failed:', e);
  }
}

// ─── Session history ──────────────────────────────────────────────────────────

async function pollSessions() {
  try {
    const res  = await fetch('/api/sessions');
    const rows = await res.json();
    const tbody = document.getElementById('session-table');
    tbody.innerHTML = rows.map(r => `
      <tr>
        <td>${r.timestamp}</td>
        <td><code>${r.uid}</code></td>
        <td><span class="badge ${r.event === 'fault' ? 'bg-danger' : 'bg-success'}">${r.event}</span></td>
        <td>${r.energy_wh != null ? r.energy_wh.toFixed(2) : '—'}</td>
        <td>${r.cost_rs   != null ? '₹ ' + r.cost_rs.toFixed(2) : '—'}</td>
        <td>${r.duration_s != null ? formatElapsed(r.duration_s) : '—'}</td>
      </tr>
    `).join('');
  } catch (e) {
    console.warn('Session poll failed:', e);
  }
}

// ─── Aggregate stats ──────────────────────────────────────────────────────────

async function pollStats() {
  try {
    const res  = await fetch('/api/stats');
    const data = await res.json();
    document.getElementById('stat-sessions').textContent = data.total_sessions;
    document.getElementById('stat-energy').textContent   = `${(data.total_energy_wh / 1000).toFixed(3)} kWh`;
    document.getElementById('stat-revenue').textContent  = `₹ ${data.total_revenue_rs.toFixed(2)}`;
    document.getElementById('stat-faults').textContent   = data.fault_count;
  } catch (e) {
    console.warn('Stats poll failed:', e);
  }
}

// ─── Bootstrap ────────────────────────────────────────────────────────────────

async function tick() {
  await Promise.all([pollLive(), pollSessions(), pollStats()]);
}

tick();
setInterval(tick, POLL_INTERVAL_MS);
