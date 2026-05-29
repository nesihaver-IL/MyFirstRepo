#!/usr/bin/env python3
"""
Windows System Monitor - Real-time monitoring with Python
Uses psutil for cross-platform system metrics
Includes web server for live dashboard updates
"""

import psutil
import platform
import datetime
import json
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser

class SystemMonitor:
    """Collect and analyze system metrics"""

    def __init__(self):
        self.platform = platform.system()

    def get_cpu_info(self):
        """Get CPU information and usage"""
        cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        cpu_freq = psutil.cpu_freq()

        return {
            'usage_percent': round(cpu_percent, 2),
            'per_core': [round(x, 2) for x in cpu_per_core],
            'logical_count': cpu_count,
            'physical_count': cpu_count_physical,
            'frequency_mhz': round(cpu_freq.current, 2) if cpu_freq else 0,
            'frequency_max': round(cpu_freq.max, 2) if cpu_freq else 0
        }

    def get_memory_info(self):
        """Get memory information"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2),
            'percent': round(mem.percent, 2),
            'swap_total_gb': round(swap.total / (1024**3), 2),
            'swap_used_gb': round(swap.used / (1024**3), 2),
            'swap_percent': round(swap.percent, 2)
        }

    def get_disk_info(self):
        """Get disk information"""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_gb': round(usage.free / (1024**3), 2),
                    'percent': round(usage.percent, 2)
                })
            except PermissionError:
                continue
        return disks

    def get_network_info(self):
        """Get network information"""
        net_io = psutil.net_io_counters()
        interfaces = []

        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == 2:  # AF_INET (IPv4)
                    interfaces.append({
                        'name': interface,
                        'ip': addr.address
                    })
                    break

        return {
            'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            'interfaces': interfaces
        }

    def get_battery_info(self):
        """Get battery information (if available)"""
        battery = psutil.sensors_battery()
        if battery:
            return {
                'percent': round(battery.percent, 2),
                'plugged': battery.power_plugged,
                'time_left_minutes': round(battery.secsleft / 60, 0) if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
            }
        return None

    def get_top_processes(self, limit=20):
        """Get top processes by CPU and memory usage"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': round(pinfo['cpu_percent'] or 0, 2),
                    'memory_mb': round(pinfo['memory_info'].rss / (1024**2), 2) if pinfo['memory_info'] else 0,
                    'memory_percent': round(pinfo['memory_percent'] or 0, 2),
                    'status': pinfo['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # Sort by memory usage
        processes.sort(key=lambda x: x['memory_mb'], reverse=True)
        return processes[:limit]

    def get_system_info(self):
        """Get general system information"""
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time

        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': platform.node(),
            'processor': platform.processor(),
            'boot_time': boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            'uptime_days': uptime.days,
            'uptime_hours': uptime.seconds // 3600,
            'uptime_minutes': (uptime.seconds % 3600) // 60
        }

    def get_all_metrics(self):
        """Gather all system metrics"""
        return {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'system': self.get_system_info(),
            'cpu': self.get_cpu_info(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info(),
            'battery': self.get_battery_info(),
            'processes': self.get_top_processes()
        }


class MonitorRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for real-time monitoring"""

    def __init__(self, *args, monitor=None, **kwargs):
        self.monitor = monitor
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/api/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            metrics = self.monitor.get_all_metrics()
            self.wfile.write(json.dumps(metrics).encode())
        else:
            super().do_GET()

    def log_message(self, format, *args):
        """Suppress server logs"""
        pass


def create_html_dashboard(output_file="windows-monitor-live.html"):
    """Create HTML dashboard with live updates"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Windows System Monitor - Live</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
            color: #fff;
        }

        .container { max-width: 1800px; margin: 0 auto; }

        header {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        h1 {
            color: #fff;
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }

        .live-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(76, 175, 80, 0.3);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.95em;
        }

        .live-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4caf50;
            animation: blink 1.5s infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; box-shadow: 0 0 10px #4caf50; }
            50% { opacity: 0.3; }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.15);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }

        .stat-card:hover { transform: translateY(-5px); }

        .stat-icon { font-size: 2.5em; margin-bottom: 10px; }
        .stat-value { font-size: 2.2em; font-weight: bold; margin-bottom: 5px; }
        .stat-label { font-size: 1em; opacity: 0.9; }
        .stat-sublabel { font-size: 0.85em; opacity: 0.7; margin-top: 5px; }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 25px;
        }

        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .card-title {
            font-size: 1.6em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        }

        .process-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }

        .process-table th {
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }

        .process-table td {
            padding: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .process-table tr:hover { background: rgba(255, 255, 255, 0.05); }

        .high-usage { color: #ff5252; font-weight: bold; }
        .medium-usage { color: #ffc107; }
        .low-usage { color: #4caf50; }

        .chart-container { position: relative; height: 300px; margin-top: 20px; }

        .timestamp {
            text-align: center;
            margin-top: 30px;
            opacity: 0.8;
        }

        .alert {
            background: rgba(255, 193, 7, 0.2);
            border: 1px solid rgba(255, 193, 7, 0.5);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🪟 Windows System Monitor - Live Dashboard</h1>
            <div style="margin-top: 10px;">
                <span class="live-indicator">
                    <span class="live-dot"></span>
                    Live Updates • Refreshing every 5 seconds
                </span>
            </div>
            <div id="systemInfo" style="margin-top: 10px; opacity: 0.9;"></div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🖥️</div>
                <div class="stat-value" id="cpuUsage">--</div>
                <div class="stat-label">CPU Usage</div>
                <div class="stat-sublabel" id="cpuCores">--</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">💾</div>
                <div class="stat-value" id="memUsage">--</div>
                <div class="stat-label">Memory Usage</div>
                <div class="stat-sublabel" id="memDetails">--</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">💿</div>
                <div class="stat-value" id="diskUsage">--</div>
                <div class="stat-label">Disk Usage (C:)</div>
                <div class="stat-sublabel" id="diskDetails">--</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">🔋</div>
                <div class="stat-value" id="batteryPercent">--</div>
                <div class="stat-label">Battery Status</div>
                <div class="stat-sublabel" id="batteryStatus">--</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">⏱️</div>
                <div class="stat-value" id="uptime">--</div>
                <div class="stat-label">System Uptime</div>
                <div class="stat-sublabel" id="bootTime">--</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">🌐</div>
                <div class="stat-value" id="networkSent">--</div>
                <div class="stat-label">Network Sent</div>
                <div class="stat-sublabel" id="networkRecv">--</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2 class="card-title">🔥 Top Resource Consumers</h2>
                <div id="processAlert" class="alert" style="display: none;"></div>
                <div style="max-height: 400px; overflow-y: auto;">
                    <table class="process-table">
                        <thead>
                            <tr>
                                <th>Process</th>
                                <th>PID</th>
                                <th>Memory (MB)</th>
                                <th>Memory %</th>
                                <th>CPU %</th>
                            </tr>
                        </thead>
                        <tbody id="processTable"></tbody>
                    </table>
                </div>
            </div>

            <div class="card">
                <h2 class="card-title">📊 Resource Distribution</h2>
                <div class="chart-container">
                    <canvas id="resourceChart"></canvas>
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2 class="card-title">💾 Memory Breakdown</h2>
                <div class="chart-container">
                    <canvas id="memoryChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2 class="card-title">🖥️ CPU Per Core</h2>
                <div class="chart-container">
                    <canvas id="cpuChart"></canvas>
                </div>
            </div>
        </div>

        <div class="timestamp">
            📅 Last Updated: <span id="timestamp">--</span>
        </div>
    </div>

    <script>
        let charts = {};

        // Initialize charts
        function initCharts() {
            // Resource Chart
            charts.resource = new Chart(document.getElementById('resourceChart').getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['CPU', 'Memory', 'Disk'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#4fc3f7', '#ff9800', '#9c27b0']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#fff' } } }
                }
            });

            // Memory Chart
            charts.memory = new Chart(document.getElementById('memoryChart').getContext('2d'), {
                type: 'bar',
                data: {
                    labels: ['Used', 'Available'],
                    datasets: [{
                        label: 'Memory (GB)',
                        data: [0, 0],
                        backgroundColor: ['#ff5252', '#4caf50']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#fff' } } },
                    scales: {
                        y: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        x: { ticks: { color: '#fff' }, grid: { display: false } }
                    }
                }
            });

            // CPU Chart
            charts.cpu = new Chart(document.getElementById('cpuChart').getContext('2d'), {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#4fc3f7',
                        backgroundColor: 'rgba(79, 195, 247, 0.2)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#fff' } } },
                    scales: {
                        y: { beginAtZero: true, max: 100, ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                        x: { ticks: { color: '#fff' }, grid: { display: false } }
                    }
                }
            });
        }

        // Update dashboard with live data
        async function updateDashboard() {
            try {
                const response = await fetch('http://localhost:8000/api/metrics');
                const data = await response.json();

                // Update stats
                document.getElementById('cpuUsage').textContent = data.cpu.usage_percent + '%';
                document.getElementById('cpuCores').textContent = data.cpu.logical_count + ' cores';

                document.getElementById('memUsage').textContent = data.memory.percent + '%';
                document.getElementById('memDetails').textContent =
                    data.memory.used_gb + ' GB / ' + data.memory.total_gb + ' GB';

                if (data.disk.length > 0) {
                    document.getElementById('diskUsage').textContent = data.disk[0].percent + '%';
                    document.getElementById('diskDetails').textContent =
                        data.disk[0].used_gb + ' GB / ' + data.disk[0].total_gb + ' GB';
                }

                if (data.battery) {
                    document.getElementById('batteryPercent').textContent = data.battery.percent + '%';
                    document.getElementById('batteryStatus').textContent =
                        data.battery.plugged ? 'Plugged In' : 'On Battery';
                } else {
                    document.getElementById('batteryPercent').textContent = 'N/A';
                    document.getElementById('batteryStatus').textContent = 'Desktop PC';
                }

                document.getElementById('uptime').textContent =
                    data.system.uptime_days + 'd ' + data.system.uptime_hours + 'h ' + data.system.uptime_minutes + 'm';
                document.getElementById('bootTime').textContent = 'Boot: ' + data.system.boot_time;

                document.getElementById('networkSent').textContent = data.network.bytes_sent_mb + ' MB';
                document.getElementById('networkRecv').textContent = 'Received: ' + data.network.bytes_recv_mb + ' MB';

                document.getElementById('systemInfo').textContent =
                    '💻 ' + data.system.hostname + ' • ' + data.system.platform + ' ' + data.system.platform_release;

                document.getElementById('timestamp').textContent = data.timestamp;

                // Update process table
                const processTable = document.getElementById('processTable');
                processTable.innerHTML = '';
                data.processes.slice(0, 15).forEach(proc => {
                    const statusClass = proc.memory_percent > 5 ? 'high-usage' :
                                      proc.memory_percent > 2 ? 'medium-usage' : 'low-usage';
                    const row = `
                        <tr>
                            <td><strong>${proc.name}</strong></td>
                            <td>${proc.pid}</td>
                            <td>${proc.memory_mb}</td>
                            <td class="${statusClass}">${proc.memory_percent}%</td>
                            <td>${proc.cpu_percent}%</td>
                        </tr>
                    `;
                    processTable.innerHTML += row;
                });

                // Show alert for top consumer
                if (data.processes.length > 0) {
                    const top = data.processes[0];
                    const alert = document.getElementById('processAlert');
                    alert.style.display = 'block';
                    alert.innerHTML = `<strong>💡 Power Consumer:</strong> <strong>${top.name}</strong> is using ${top.memory_mb} MB (${top.memory_percent}%)`;
                }

                // Update charts
                charts.resource.data.datasets[0].data = [
                    data.cpu.usage_percent,
                    data.memory.percent,
                    data.disk[0]?.percent || 0
                ];
                charts.resource.update();

                charts.memory.data.datasets[0].data = [
                    data.memory.used_gb,
                    data.memory.available_gb
                ];
                charts.memory.update();

                // Update CPU timeline
                const now = new Date().toLocaleTimeString();
                if (charts.cpu.data.labels.length > 20) {
                    charts.cpu.data.labels.shift();
                    charts.cpu.data.datasets[0].data.shift();
                }
                charts.cpu.data.labels.push(now);
                charts.cpu.data.datasets[0].data.push(data.cpu.usage_percent);
                charts.cpu.update();

            } catch (error) {
                console.error('Error fetching metrics:', error);
            }
        }

        // Initialize and start updates
        initCharts();
        updateDashboard();
        setInterval(updateDashboard, 5000); // Update every 5 seconds
    </script>
</body>
</html>'''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Live dashboard created: {output_file}")
    return output_file


def start_monitor_server(port=8000):
    """Start HTTP server for real-time monitoring"""
    monitor = SystemMonitor()

    def handler(*args, **kwargs):
        MonitorRequestHandler(*args, monitor=monitor, **kwargs)

    server = HTTPServer(('localhost', port), handler)
    print(f"🌐 Starting monitoring server on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("🪟 Windows System Monitor - Python Edition")
    print("=" * 60)

    # Create HTML dashboard
    dashboard_file = create_html_dashboard()

    # Choose mode
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        print("\n📊 Starting LIVE monitoring mode...")
        print("   Dashboard will update every 5 seconds")
        print("   Press Ctrl+C to stop\n")

        # Start server in background thread
        server_thread = threading.Thread(target=start_monitor_server, daemon=True)
        server_thread.start()

        time.sleep(1)

        # Open browser
        dashboard_path = Path(dashboard_file).absolute()
        webbrowser.open(f'file://{dashboard_path}')
        print(f"✅ Dashboard opened: {dashboard_path}")
        print("\n💡 Keep this terminal open for live updates!")
        print("   Server running at: http://localhost:8000/api/metrics\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 Shutting down monitor...")
            sys.exit(0)

    else:
        print("\n📸 Running SNAPSHOT mode...")
        monitor = SystemMonitor()
        metrics = monitor.get_all_metrics()

        print(f"\n📊 System Metrics Snapshot:")
        print(f"   Hostname: {metrics['system']['hostname']}")
        print(f"   Platform: {metrics['system']['platform']} {metrics['system']['platform_release']}")
        print(f"   CPU Usage: {metrics['cpu']['usage_percent']}%")
        print(f"   Memory: {metrics['memory']['used_gb']} GB / {metrics['memory']['total_gb']} GB ({metrics['memory']['percent']}%)")
        print(f"   Top Process: {metrics['processes'][0]['name']} ({metrics['processes'][0]['memory_mb']} MB)")

        print(f"\n💡 Tip: Run with --live flag for real-time monitoring:")
        print(f"   python system_monitor.py --live\n")
