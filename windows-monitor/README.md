# 🪟 Windows System Monitor

**Real-time Windows system monitoring dashboard** with power consumption analysis. Monitor CPU, memory, disk usage, running processes, and identify resource-hungry applications on your Windows machine.

## 🎯 Features

✅ **Real-time Monitoring**
- Live CPU, Memory, and Disk usage tracking
- Process-level resource consumption
- Network statistics
- Battery status (for laptops)
- System uptime and boot time

✅ **Power Analysis**
- Identify top resource consumers
- Highlight power-hungry processes
- Memory usage breakdown per process
- CPU usage per core

✅ **Beautiful Dashboards**
- Interactive charts with Chart.js
- Auto-refreshing displays
- Responsive design
- Color-coded indicators

✅ **Two Implementations**
- **PowerShell**: Native Windows, no dependencies
- **Python**: Cross-platform, real-time updates

## 📦 What's Included

```
windows-monitor/
├── Get-WindowsSystemMonitor.ps1    # PowerShell script (Windows native)
├── system_monitor.py                # Python script (cross-platform)
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🚀 Quick Start

### Option 1: PowerShell (Recommended for Windows)

**No installation required!** Just run:

```powershell
# Basic usage
.\Get-WindowsSystemMonitor.ps1

# Open dashboard automatically in browser
.\Get-WindowsSystemMonitor.ps1 -OpenBrowser

# Specify custom output file
.\Get-WindowsSystemMonitor.ps1 -OutputPath "C:\Monitoring\dashboard.html"

# Show top 20 processes instead of default 15
.\Get-WindowsSystemMonitor.ps1 -TopProcesses 20 -OpenBrowser
```

**First-time setup:**
If you get an execution policy error, run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Option 2: Python (Cross-platform + Live Updates)

**Installation:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install directly
pip install psutil
```

**Usage:**

```bash
# Snapshot mode - Generate dashboard once
python system_monitor.py

# Live mode - Real-time updates every 5 seconds
python system_monitor.py --live
```

## 📊 Dashboard Features

### PowerShell Dashboard
- **Static snapshot** of current system state
- **Auto-refresh** every 30 seconds (HTML meta refresh)
- Top 15 resource-consuming processes
- System information and metrics
- Battery status (if laptop)
- Network statistics

### Python Dashboard
- **Live updates** every 5 seconds
- **Real-time charts** with historical data
- Interactive process table
- CPU usage timeline
- Auto-opens in default browser
- REST API endpoint for custom integrations

## 🖥️ System Requirements

### PowerShell Script
- **OS**: Windows 10/11, Windows Server 2016+
- **PowerShell**: 5.1 or later (built into Windows)
- **Privileges**: No admin rights required
- **Dependencies**: None

### Python Script
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.7 or later
- **Dependencies**: psutil
- **Privileges**: No admin rights required

## 📈 Metrics Monitored

| Metric | PowerShell | Python Live |
|--------|-----------|-------------|
| CPU Usage (Total) | ✅ | ✅ |
| CPU Usage (Per Core) | ❌ | ✅ |
| Memory Usage | ✅ | ✅ |
| Swap/Pagefile Usage | ❌ | ✅ |
| Disk Usage | ✅ (C: only) | ✅ (All drives) |
| Network Traffic | ✅ | ✅ |
| Battery Status | ✅ | ✅ |
| Top Processes | ✅ | ✅ |
| Running Services | ✅ | ❌ |
| System Uptime | ✅ | ✅ |
| Real-time Updates | ❌ | ✅ |

## 🎨 Dashboard Previews

### Metrics Displayed
- **CPU Usage**: Overall percentage and per-core breakdown
- **Memory**: Used vs. Available (GB and %)
- **Disk**: Space used on all drives
- **Battery**: Charge level and status (AC/Battery)
- **Network**: Data sent/received
- **Uptime**: Days, hours, minutes since last boot
- **Processes**: Top 15-20 by memory usage with PID and CPU%

### Visual Indicators
- 🟢 **Green**: Low usage (<2%)
- 🟡 **Yellow**: Medium usage (2-5%)
- 🔴 **Red**: High usage (>5%) - **Power consumers highlighted!**

## 🔧 Advanced Usage

### Schedule PowerShell Monitoring

Create a scheduled task to run every hour:

```powershell
# Create scheduled task (run as Administrator)
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\Path\To\Get-WindowsSystemMonitor.ps1 -OutputPath C:\Monitoring\dashboard.html"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName "SystemMonitor" -Action $action -Trigger $trigger
```

### Python API Endpoint

When running in live mode, Python exposes metrics via REST API:

```bash
# Get JSON metrics
curl http://localhost:8000/api/metrics
```

**Response format:**
```json
{
  "timestamp": "2026-01-09 15:30:00",
  "system": { "hostname": "...", "platform": "Windows", ... },
  "cpu": { "usage_percent": 15.2, "logical_count": 16, ... },
  "memory": { "total_gb": 16.0, "used_gb": 8.5, "percent": 53.1 },
  "processes": [
    { "name": "chrome.exe", "pid": 1234, "memory_mb": 512.3, ... }
  ]
}
```

### Custom Integration

You can build custom dashboards or integrate with monitoring tools:

```python
import requests

# Fetch metrics
response = requests.get('http://localhost:8000/api/metrics')
data = response.json()

# Analyze
if data['cpu']['usage_percent'] > 80:
    print("⚠️ High CPU usage detected!")

# Find top consumer
top_process = data['processes'][0]
print(f"Top consumer: {top_process['name']} using {top_process['memory_mb']} MB")
```

## 🐛 Troubleshooting

### PowerShell: "Execution policy error"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python: "ModuleNotFoundError: No module named 'psutil'"
```bash
pip install psutil
```

### Python Live Mode: Browser doesn't open
Manually navigate to: `file:///path/to/windows-monitor-live.html`

### Dashboard not updating in live mode
- Ensure Python script is still running
- Check that port 8000 is not blocked by firewall
- Verify API endpoint is accessible: http://localhost:8000/api/metrics

## 💡 Tips

1. **PowerShell for quick checks**: Use when you need a fast snapshot without installing anything
2. **Python for continuous monitoring**: Use when you need real-time tracking and historical data
3. **Schedule PowerShell script**: Set up Windows Task Scheduler for automated monitoring
4. **Multiple monitors**: Run both scripts to compare results and validate accuracy
5. **Battery drain analysis**: Use laptop battery metrics to identify power-hungry apps

## 🔐 Security & Privacy

- ✅ No data leaves your computer
- ✅ No internet connection required
- ✅ No telemetry or tracking
- ✅ No admin privileges needed
- ✅ Open source - inspect the code yourself

## 📝 Output Files

### PowerShell
- **Default**: `windows-system-monitor.html` (in current directory)
- **Custom**: Use `-OutputPath` parameter

### Python
- **Snapshot**: Prints to console
- **Live**: Creates `windows-monitor-live.html` + runs web server on port 8000

## 🎯 Use Cases

✅ **Identify resource hogs**: Find which apps are slowing down your PC
✅ **Monitor system health**: Track CPU, memory, disk usage trends
✅ **Battery optimization**: Identify power-hungry processes on laptops
✅ **Performance troubleshooting**: Debug slowdowns and freezes
✅ **Capacity planning**: Determine if you need more RAM/CPU
✅ **Process management**: See what's running and using resources

## 📚 Examples

### Find Chrome's memory usage
```powershell
.\Get-WindowsSystemMonitor.ps1
# Open dashboard, look for chrome.exe in process table
```

### Monitor during video rendering
```bash
python system_monitor.py --live
# Watch CPU/Memory usage in real-time while rendering
```

### Identify battery drain on laptop
```powershell
.\Get-WindowsSystemMonitor.ps1 -OpenBrowser
# Check battery status and top processes
# High CPU/Memory processes = faster battery drain
```

## 🤝 Contributing

Found a bug? Want to add a feature? Contributions welcome!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [psutil](https://github.com/giampaolo/psutil) for Python metrics
- Charts powered by [Chart.js](https://www.chartjs.org/)
- Designed for Windows system administrators and power users

---

**Happy Monitoring!** 🖥️📊

For questions or issues, please create an issue in the repository.
