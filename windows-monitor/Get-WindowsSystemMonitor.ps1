# Windows System Monitor
# PowerShell script to gather system metrics and generate HTML dashboard

param(
    [string]$OutputPath = "windows-system-monitor.html",
    [int]$TopProcesses = 15,
    [switch]$OpenBrowser
)

Write-Host "🔍 Gathering Windows System Information..." -ForegroundColor Cyan

# Get System Information
$computerSystem = Get-CimInstance Win32_ComputerSystem
$operatingSystem = Get-CimInstance Win32_OperatingSystem
$processor = Get-CimInstance Win32_Processor | Select-Object -First 1
$physicalMemory = Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum

# Get CPU Usage
$cpuUsage = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
$cpuUsage = [math]::Round($cpuUsage, 2)

# Get Memory Information
$totalMemoryGB = [math]::Round($physicalMemory.Sum / 1GB, 2)
$freeMemoryGB = [math]::Round($operatingSystem.FreePhysicalMemory / 1MB, 2)
$usedMemoryGB = [math]::Round($totalMemoryGB - $freeMemoryGB, 2)
$memoryUsagePercent = [math]::Round(($usedMemoryGB / $totalMemoryGB) * 100, 2)

# Get Disk Information
$disk = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" | Where-Object {$_.DeviceID -eq "C:"}
$totalDiskGB = [math]::Round($disk.Size / 1GB, 2)
$freeDiskGB = [math]::Round($disk.FreeSpace / 1GB, 2)
$usedDiskGB = [math]::Round($totalDiskGB - $freeDiskGB, 2)
$diskUsagePercent = [math]::Round(($usedDiskGB / $totalDiskGB) * 100, 2)

# Get Uptime
$uptime = (Get-Date) - $operatingSystem.LastBootUpTime
$uptimeString = "{0}d {1}h {2}m" -f $uptime.Days, $uptime.Hours, $uptime.Minutes

# Get Top Processes by CPU and Memory
Write-Host "📊 Analyzing running processes..." -ForegroundColor Yellow
$processes = Get-Process | Where-Object {$_.CPU -ne $null} |
    Select-Object Name, Id,
        @{Name="CPU";Expression={[math]::Round($_.CPU, 2)}},
        @{Name="MemoryMB";Expression={[math]::Round($_.WorkingSet / 1MB, 2)}},
        @{Name="MemoryPercent";Expression={[math]::Round(($_.WorkingSet / ($totalMemoryGB * 1GB)) * 100, 2)}} |
    Sort-Object MemoryMB -Descending |
    Select-Object -First $TopProcesses

# Get Windows Services
$runningServices = (Get-Service | Where-Object {$_.Status -eq "Running"}).Count
$totalServices = (Get-Service).Count

# Get Network Adapters
$networkAdapters = Get-NetAdapter | Where-Object {$_.Status -eq "Up"}

# Battery Information (if laptop)
$battery = Get-CimInstance Win32_Battery
$hasBattery = $battery -ne $null
if ($hasBattery) {
    $batteryPercent = $battery.EstimatedChargeRemaining
    $batteryStatus = switch ($battery.BatteryStatus) {
        1 { "Discharging" }
        2 { "AC Power" }
        3 { "Fully Charged" }
        4 { "Low" }
        5 { "Critical" }
        default { "Unknown" }
    }
} else {
    $batteryPercent = 0
    $batteryStatus = "No Battery (Desktop)"
}

# Generate Process Data for Charts
$processesJson = $processes | ConvertTo-Json -Compress
$processNames = ($processes | Select-Object -First 10).Name -join '","'
$processMemory = ($processes | Select-Object -First 10).MemoryMB -join ','

# Get Current Date/Time
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "✅ Data collection complete!" -ForegroundColor Green
Write-Host "📝 Generating HTML dashboard..." -ForegroundColor Cyan

# Generate HTML Dashboard
$htmlContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="30">
    <title>Windows System Monitor - $($computerSystem.Name)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 20px;
            min-height: 100vh;
            color: #fff;
        }

        .container { max-width: 1600px; margin: 0 auto; }

        header {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }

        h1 {
            color: #4fc3f7;
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            text-shadow: 0 0 20px rgba(79, 195, 247, 0.5);
        }

        h1::before { content: "🪟"; margin-right: 15px; }

        .system-info {
            color: #b3e5fc;
            font-size: 1.1em;
            margin-top: 10px;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(76, 175, 80, 0.3);
            padding: 8px 16px;
            border-radius: 20px;
            margin-top: 10px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4caf50;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.3); opacity: 0.7; }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, rgba(79, 195, 247, 0.2), rgba(41, 182, 246, 0.2));
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            transition: transform 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(79, 195, 247, 0.4);
        }

        .stat-icon { font-size: 2.5em; margin-bottom: 10px; }
        .stat-value { font-size: 2.2em; font-weight: bold; color: #4fc3f7; margin-bottom: 5px; }
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
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .card-title {
            font-size: 1.6em;
            color: #4fc3f7;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(79, 195, 247, 0.3);
            display: flex;
            align-items: center;
        }

        .card-title .icon { margin-right: 10px; }

        .process-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        .process-table th {
            background: rgba(79, 195, 247, 0.2);
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid rgba(79, 195, 247, 0.5);
        }

        .process-table td {
            padding: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .process-table tr:hover {
            background: rgba(79, 195, 247, 0.1);
        }

        .high-usage { color: #ff5252; font-weight: bold; }
        .medium-usage { color: #ffc107; }
        .low-usage { color: #4caf50; }

        .chart-container { position: relative; height: 300px; margin-top: 20px; }

        .alert {
            background: rgba(255, 152, 0, 0.2);
            border: 1px solid rgba(255, 152, 0, 0.5);
            padding: 15px;
            border-radius: 10px;
            margin: 15px 0;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .refresh-btn {
            background: linear-gradient(135deg, #4fc3f7, #29b6f6);
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            margin-left: 15px;
            transition: all 0.3s ease;
        }

        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(79, 195, 247, 0.5);
        }

        .timestamp {
            text-align: center;
            color: #b3e5fc;
            margin-top: 30px;
            font-size: 0.95em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Windows System Monitor</h1>
            <div class="system-info">
                💻 $($computerSystem.Name) • $($operatingSystem.Caption) • $($processor.Name)
            </div>
            <div class="status-badge">
                <span class="status-dot"></span>
                System Active • Auto-refresh: 30s
                <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Now</button>
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-icon">🖥️</div>
                <div class="stat-value">$cpuUsage%</div>
                <div class="stat-label">CPU Usage</div>
                <div class="stat-sublabel">$($processor.NumberOfLogicalProcessors) logical cores</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">💾</div>
                <div class="stat-value">$memoryUsagePercent%</div>
                <div class="stat-label">Memory Usage</div>
                <div class="stat-sublabel">$usedMemoryGB GB / $totalMemoryGB GB</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">💿</div>
                <div class="stat-value">$diskUsagePercent%</div>
                <div class="stat-label">Disk Usage (C:)</div>
                <div class="stat-sublabel">$usedDiskGB GB / $totalDiskGB GB</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">⚙️</div>
                <div class="stat-value">$runningServices</div>
                <div class="stat-label">Running Services</div>
                <div class="stat-sublabel">of $totalServices total services</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">⏱️</div>
                <div class="stat-value">$uptimeString</div>
                <div class="stat-label">System Uptime</div>
                <div class="stat-sublabel">Last boot: $($operatingSystem.LastBootUpTime.ToString("MMM dd, HH:mm"))</div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">🔋</div>
                <div class="stat-value">$batteryPercent%</div>
                <div class="stat-label">Battery Status</div>
                <div class="stat-sublabel">$batteryStatus</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2 class="card-title"><span class="icon">🔥</span>Top Resource Consumers</h2>
                <table class="process-table">
                    <thead>
                        <tr>
                            <th>Process Name</th>
                            <th>PID</th>
                            <th>Memory (MB)</th>
                            <th>Memory %</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
"@

# Add process rows
foreach ($proc in $processes) {
    $statusClass = if ($proc.MemoryPercent -gt 5) { "high-usage" }
                   elseif ($proc.MemoryPercent -gt 2) { "medium-usage" }
                   else { "low-usage" }

    $statusText = if ($proc.MemoryPercent -gt 5) { "⚠️ HIGH" }
                  elseif ($proc.MemoryPercent -gt 2) { "⚡ MEDIUM" }
                  else { "✅ LOW" }

    $htmlContent += @"
                        <tr>
                            <td><strong>$($proc.Name)</strong></td>
                            <td>$($proc.Id)</td>
                            <td>$($proc.MemoryMB)</td>
                            <td class="$statusClass">$($proc.MemoryPercent)%</td>
                            <td class="$statusClass">$statusText</td>
                        </tr>
"@
}

$htmlContent += @"
                    </tbody>
                </table>

                <div class="alert">
                    <span style="font-size: 2em;">💡</span>
                    <div>
                        <strong>Power Analysis:</strong> Top consumer is <strong>$($processes[0].Name)</strong>
                        using $($processes[0].MemoryMB) MB of memory ($($processes[0].MemoryPercent)%).
                    </div>
                </div>
            </div>

            <div class="card">
                <h2 class="card-title"><span class="icon">📊</span>Memory Distribution</h2>
                <div class="chart-container">
                    <canvas id="memoryChart"></canvas>
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2 class="card-title"><span class="icon">💾</span>Top 10 Processes by Memory</h2>
                <div class="chart-container">
                    <canvas id="processChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2 class="card-title"><span class="icon">🖥️</span>System Resource Overview</h2>
                <div class="chart-container">
                    <canvas id="resourceChart"></canvas>
                </div>
            </div>
        </div>

        <div class="timestamp">
            📅 Last Updated: $timestamp • Running on Windows PowerShell
        </div>
    </div>

    <script>
        // Memory Distribution Chart
        const memoryCtx = document.getElementById('memoryChart').getContext('2d');
        new Chart(memoryCtx, {
            type: 'doughnut',
            data: {
                labels: ['Used Memory', 'Free Memory'],
                datasets: [{
                    data: [$usedMemoryGB, $freeMemoryGB],
                    backgroundColor: ['rgba(255, 82, 82, 0.8)', 'rgba(76, 175, 80, 0.8)'],
                    borderColor: ['#ff5252', '#4caf50'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#fff', font: { size: 14 } } },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.toFixed(2) + ' GB';
                            }
                        }
                    }
                }
            }
        });

        // Process Memory Chart
        const processCtx = document.getElementById('processChart').getContext('2d');
        new Chart(processCtx, {
            type: 'bar',
            data: {
                labels: ["$processNames"],
                datasets: [{
                    label: 'Memory Usage (MB)',
                    data: [$processMemory],
                    backgroundColor: 'rgba(79, 195, 247, 0.8)',
                    borderColor: '#4fc3f7',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: '#fff' } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#fff' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#fff', maxRotation: 45, minRotation: 45 }
                    }
                }
            }
        });

        // Resource Overview Chart
        const resourceCtx = document.getElementById('resourceChart').getContext('2d');
        new Chart(resourceCtx, {
            type: 'bar',
            data: {
                labels: ['CPU Usage', 'Memory Usage', 'Disk Usage'],
                datasets: [{
                    label: 'Usage (%)',
                    data: [$cpuUsage, $memoryUsagePercent, $diskUsagePercent],
                    backgroundColor: [
                        'rgba(79, 195, 247, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(156, 39, 176, 0.8)'
                    ],
                    borderColor: ['#4fc3f7', '#ff9800', '#9c27b0'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#fff' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#fff' }
                    }
                }
            }
        });
    </script>
</body>
</html>
"@

# Save HTML file
$htmlContent | Out-File -FilePath $OutputPath -Encoding UTF8

Write-Host "✅ Dashboard generated successfully!" -ForegroundColor Green
Write-Host "📄 File saved to: $OutputPath" -ForegroundColor Cyan

if ($OpenBrowser) {
    Write-Host "🌐 Opening in default browser..." -ForegroundColor Yellow
    Start-Process $OutputPath
}

Write-Host "`n💡 Tip: Run this script regularly or set up a scheduled task for automatic monitoring!" -ForegroundColor Magenta
Write-Host "   Example: .\Get-WindowsSystemMonitor.ps1 -OpenBrowser`n" -ForegroundColor White
