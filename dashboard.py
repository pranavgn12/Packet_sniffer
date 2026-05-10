from flask import Flask, request, jsonify, render_template_string
import requests
import argparse

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IDS Security Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    /* Modern Light Theme Variables */
    :root {
      --bg-body: #f8fafc;
      --bg-panel: #ffffff;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --border-color: #e2e8f0;

      --brand-primary: #4f46e5;

      /* Attack Category Colors */
      --c-normal: #10b981;    /* Green */
      --c-recon: #f59e0b;     /* Orange */
      --c-dos: #ef4444;       /* Red */
      --c-fuzzer: #3b82f6;    /* Blue */
      --c-exploit: #8b5cf6;   /* Purple */
      --c-generic: #64748b;   /* Gray */
      --c-backdoor: #14b8a6;  /* Teal */
      --c-shellcode: #ec4899; /* Pink */
      --c-worms: #eab308;     /* Yellow */
      --c-analysis: #6366f1;  /* Indigo */
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: 'Inter', sans-serif;
      background-color: var(--bg-body);
      color: var(--text-main);
      -webkit-font-smoothing: antialiased;
    }

    /* Header styling using Flexbox */
    .header {
      background-color: var(--bg-panel);
      padding: 20px 32px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .header h1 {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--brand-primary);
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .badge {
      background-color: #e0e7ff;
      color: var(--brand-primary);
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }

    /* Main layout container */
    .container {
      display: flex;
      gap: 24px;
      padding: 32px;
      max-width: 1600px;
      margin: 0 auto;
    }

    /* Sidebar for controls */
    .sidebar {
      width: 320px;
      flex-shrink: 0;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    /* Reusable Panel Class */
    .panel {
      background: var(--bg-panel);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -2px rgba(0, 0, 0, 0.02);
    }

    .panel-title {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 20px;
      color: var(--text-main);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    /* Attack Controls using CSS Grid */
    .control-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .btn {
      padding: 10px 12px;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      color: white;
      font-weight: 500;
      font-size: 0.875rem;
      font-family: inherit;
      transition: all 0.2s ease;
      background: var(--c-generic);
    }

    .btn:hover { transform: translateY(-1px); box-shadow: 0 4px 6px rgba(0,0,0,0.1); filter: brightness(110%); }
    .btn:active { transform: translateY(0); }
    .btn.full { grid-column: span 2; }

    /* Button Colors */
    .btn.normal { background: var(--c-normal); }
    .btn.recon { background: var(--c-recon); }
    .btn.dos { background: var(--c-dos); }
    .btn.fuzzer { background: var(--c-fuzzer); }
    .btn.exploits { background: var(--c-exploit); }
    .btn.generic { background: var(--c-generic); }
    .btn.backdoor { background: var(--c-backdoor); }
    .btn.shellcode { background: var(--c-shellcode); }
    .btn.worms { background: var(--c-worms); color: #422006; } /* Dark text for contrast on yellow */
    .btn.analysis { background: var(--c-analysis); }

    .status-bar {
      margin-top: 20px;
      padding: 12px;
      background: var(--bg-body);
      border-radius: 8px;
      font-size: 0.875rem;
      color: var(--text-muted);
      text-align: center;
      border: 1px dashed var(--border-color);
    }

    /* Main Content Area */
    .main-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 24px;
      min-width: 0;
    }

    /* Top Metrics using Grid */
    .metrics-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 24px;
    }

    .metric-card {
      background: var(--bg-panel);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .metric-label { font-size: 0.875rem; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { font-size: 2.25rem; font-weight: 700; margin-top: 8px; color: var(--text-main); }
    .metric-sub { font-size: 0.875rem; color: var(--text-muted); margin-top: 4px; }

    /* Charts & Logs Area */
    .data-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    .chart-container {
      position: relative;
      height: 300px;
      width: 100%;
    }

    /* Custom Scrollbar for Logs Table */
    .table-wrapper {
      height: 300px;
      overflow-y: auto;
      border: 1px solid var(--border-color);
      border-radius: 12px;
    }

    .table-wrapper::-webkit-scrollbar { width: 8px; }
    .table-wrapper::-webkit-scrollbar-track { background: var(--bg-body); }
    .table-wrapper::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.875rem;
    }

    th {
      position: sticky;
      top: 0;
      background: #f1f5f9;
      padding: 12px 16px;
      color: var(--text-muted);
      font-weight: 600;
      border-bottom: 1px solid var(--border-color);
      z-index: 10;
    }

    td {
      padding: 12px 16px;
      border-bottom: 1px solid var(--border-color);
      color: var(--text-main);
    }

    tr:hover td { background: var(--bg-body); }
    tr:last-child td { border-bottom: none; }

    /* Classification Tag Colors */
    .tag {
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
    }

    .tag.normal { background: #dcfce7; color: #166534; }
    .tag.recon { background: #fef3c7; color: #92400e; }
    .tag.dos { background: #fee2e2; color: #991b1b; }
    .tag.fuzzer { background: #dbeafe; color: #1e40af; }
    .tag.exploits { background: #ede9fe; color: #5b21b6; }
    .tag.generic { background: #f1f5f9; color: #334155; }
    .tag.backdoor { background: #ccfbf1; color: #115e59; }
    .tag.shellcode { background: #fce7f3; color: #9d174d; }
    .tag.worms { background: #fef08a; color: #854d0e; }
    .tag.analysis { background: #e0e7ff; color: #3730a3; }

    /* Responsive Design */
    @media (max-width: 1024px) {
      .container { flex-direction: column; }
      .sidebar { width: 100%; }
      .data-row { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <header class="header">
    <h1>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
      Security Dashboard
    </h1>
    <span class="badge">Live Monitoring</span>
  </header>

  <div class="container">

    <!-- Sidebar Controls -->
    <div class="sidebar">
      <div class="panel">
        <div class="panel-title">Traffic Generator</div>
        <div class="control-grid">
          <button class="btn full normal" onclick="triggerAttack('normal')">Normal Traffic</button>
          <button class="btn recon" onclick="triggerAttack('Reconnaissance')">Reconnaissance</button>
          <button class="btn dos" onclick="triggerAttack('DoS')">Denial of Service</button>
          <button class="btn fuzzer" onclick="triggerAttack('Fuzzers')">Fuzzers</button>
          <button class="btn exploits" onclick="triggerAttack('Exploits')">Exploits</button>
          <button class="btn generic" onclick="triggerAttack('Generic')">Generic</button>
          <button class="btn backdoor" onclick="triggerAttack('Backdoor')">Backdoor</button>
          <button class="btn shellcode" onclick="triggerAttack('Shellcode')">Shellcode</button>
          <button class="btn worms" onclick="triggerAttack('Worms')">Worms</button>
          <button class="btn full analysis" onclick="triggerAttack('Analysis')">Analysis</button>
        </div>
        <div class="status-bar" id="status">System Ready.</div>
      </div>
    </div>

    <!-- Main Dashboard -->
    <div class="main-content">

      <!-- Metrics -->
      <div class="metrics-row">
        <div class="metric-card">
          <div class="metric-label">Total Predictions</div>
          <div class="metric-value" id="total">0</div>
          <div class="metric-sub">Processed packets</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Latest Prediction</div>
          <div class="metric-value" id="latest" style="color: var(--brand-primary);">-</div>
          <div class="metric-sub">Classification output</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Model Confidence</div>
          <div class="metric-value" id="confidence">-</div>
          <div class="metric-sub">Accuracy probability</div>
        </div>
      </div>

      <!-- Data Row -->
      <div class="data-row">
        <div class="panel">
          <div class="panel-title">Traffic Distribution</div>
          <div class="chart-container">
            <canvas id="chart"></canvas>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">
            Real-Time Logs
            <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: normal;">Newest first</span>
          </div>
          <div class="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Classification</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody id="logs"></tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  </div>

<script>
let chart;

// Dictionary mapping for Chart.js Hex Background Colors
const chartColors = {
  'normal': '#10b981',
  'recon': '#f59e0b',
  'dos': '#ef4444',
  'fuzzer': '#3b82f6',
  'exploits': '#8b5cf6',
  'generic': '#64748b',
  'backdoor': '#14b8a6',
  'shellcode': '#ec4899',
  'worms': '#eab308',
  'analysis': '#6366f1'
};

async function triggerAttack(cat) {
  const statusEl = document.getElementById("status");
  statusEl.innerText = `Injecting ${cat} traffic...`;
  statusEl.style.color = "var(--brand-primary)";

  try {
    const r = await fetch("/api/trigger/" + encodeURIComponent(cat), { method: "POST" });
    const j = await r.json();
    statusEl.innerText = j.message || j.error || "Injection complete.";
    statusEl.style.color = j.error ? "var(--danger)" : "var(--c-normal)";
  } catch (err) {
    statusEl.innerText = "Error connecting to backend.";
    statusEl.style.color = "var(--danger)";
  }

  setTimeout(() => {
    statusEl.style.color = "var(--text-muted)";
    statusEl.innerText = "System Ready.";
    refreshAll();
  }, 2000);
}

function fmtTime(ts) {
  if (!ts) return "-";
  const date = new Date(ts * 1000);
  return date.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' }) + '.' + date.getMilliseconds().toString().padStart(3, '0');
}

// Map the prediction string robustly to a unified key
function getCategoryKey(prediction) {
  const p = prediction.toLowerCase();
  if (p.includes('normal')) return 'normal';
  if (p.includes('recon')) return 'recon';
  if (p.includes('dos') || p.includes('denial')) return 'dos';
  if (p.includes('fuzz')) return 'fuzzer';
  if (p.includes('exploit')) return 'exploits';
  if (p.includes('backdoor')) return 'backdoor';
  if (p.includes('shellcode')) return 'shellcode';
  if (p.includes('worm')) return 'worms';
  if (p.includes('analysis')) return 'analysis';
  return 'generic';
}

function getTagClass(prediction) {
  return getCategoryKey(prediction); // Keys directly map to our CSS tag classes
}

async function refreshAll() {
  try {
    const [statsRes, historyRes] = await Promise.all([
      fetch("/api/stats"),
      fetch("/api/history?limit=50")
    ]);

    const stats = await statsRes.json();
    const history = await historyRes.json();

    // Update Top Metrics
    document.getElementById("total").innerText = stats.total ?? 0;
    document.getElementById("latest").innerText = stats.latest ? stats.latest.prediction : "-";
    document.getElementById("confidence").innerText = stats.latest ? (stats.latest.confidence * 100).toFixed(2) + "%" : "-";

    // Update Chart with Dynamic Colors
    const counts = stats.counts || {};
    const labels = Object.keys(counts);
    const values = Object.values(counts);
    const bgColors = labels.map(label => chartColors[getCategoryKey(label)] || chartColors['generic']);

    const ctx = document.getElementById("chart").getContext("2d");
    if (!chart) {
      chart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{
            label: "Classified Events",
            data: values,
            backgroundColor: bgColors,
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, grid: { color: "#e2e8f0" }, border: { dash: [4, 4] } },
            x: { grid: { display: false } }
          }
        }
      });
    } else {
      chart.data.labels = labels;
      chart.data.datasets[0].data = values;
      chart.data.datasets[0].backgroundColor = bgColors;
      chart.update();
    }

    // Update Table Logs (Explicitly sort by timestamp descending to put newest on top)
    const items = history.items || [];
    const sortedItems = items.sort((a, b) => b.timestamp - a.timestamp);

    const rows = sortedItems.map(item => {
      const pClass = getTagClass(item.prediction);
      return `
        <tr>
          <td style="font-family: monospace; color: var(--text-muted);">${fmtTime(item.timestamp)}</td>
          <td><span class="tag ${pClass}">${item.prediction}</span></td>
          <td style="font-weight: 500;">${(item.confidence * 100).toFixed(1)}%</td>
        </tr>
      `;
    }).join("");

    document.getElementById("logs").innerHTML = rows || "<tr><td colspan='3' style='text-align: center; color: var(--text-muted);'>No logged events</td></tr>";

  } catch (error) {
    console.error("Error fetching dashboard data:", error);
  }
}

// Initial fetch and polling
refreshAll();
setInterval(refreshAll, 2500);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.post("/api/trigger/<category>")
def api_trigger(category):
    url = f"http://{app.config['ATTACKER_IP']}:{app.config['ATTACKER_PORT']}/run"
    try:
        r = requests.post(url, json={
            "category": category,
            "victim_ip": app.config['VICTIM_IP'],
            "victim_port": app.config['VICTIM_PORT']
        }, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": f"Failed to reach attacker API: {str(e)}"}), 500

@app.get("/api/history")
def api_history():
    limit = int(request.args.get("limit", 50))
    url = f"http://{app.config['VICTIM_IP']}:{app.config['VICTIM_PORT']}/history?limit={limit}"
    try:
        r = requests.get(url, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        # Return empty safe object if victim is down
        return jsonify({"items": [], "error": str(e)}), 500

@app.get("/api/stats")
def api_stats():
    url = f"http://{app.config['VICTIM_IP']}:{app.config['VICTIM_PORT']}/stats"
    try:
        r = requests.get(url, timeout=10)
        return jsonify(r.json()), r.status_code
    except Exception as e:
        # Return empty safe object if victim is down
        return jsonify({"total": 0, "latest": None, "counts": {}, "error": str(e)}), 500

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attacker-ip", required=True)
    parser.add_argument("--attacker-port", type=int, default=9000)
    parser.add_argument("--victim-ip", required=True)
    parser.add_argument("--victim-port", type=int, default=8000)
    args = parser.parse_args()

    # Store configurations in the app config dictionary rather than globals
    app.config['ATTACKER_IP'] = args.attacker_ip
    app.config['ATTACKER_PORT'] = args.attacker_port
    app.config['VICTIM_IP'] = args.victim_ip
    app.config['VICTIM_PORT'] = args.victim_port

    # Run the server
    app.run(host="0.0.0.0", port=5000, debug=False)
