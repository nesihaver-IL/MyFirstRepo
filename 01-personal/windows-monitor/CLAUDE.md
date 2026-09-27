# Windows System Monitor — AI Context

## Project Purpose
Real-time Windows system monitoring dashboard with power consumption analysis.
Two implementations: PowerShell (native, no deps) and Python (cross-platform, live updates).

## Tech Stack
- **PowerShell**: `Get-WindowsSystemMonitor.ps1` — generates static HTML dashboard
- **Python**: `system_monitor.py` — live updates via REST API on port 8000 + `psutil`
- **Output**: `system-dashboard.html` (static), `os-system-monitor.html`

## Files
| File | Purpose |
|------|---------|
| `Get-WindowsSystemMonitor.ps1` | PowerShell monitor (Windows native) |
| `Find-WindowsPath.ps1` | Path resolution utility |
| `FIND_WINDOWS_PATH.bat` | Batch launcher |
| `system_monitor.py` | Python live monitor |
| `disk_analyzer.py` | Disk-specific analysis |
| `system-dashboard.html` | Static HTML dashboard template |
| `os-system-monitor.html` | OS monitor dashboard |
| `run-monitor.bat` | Batch launcher for Python monitor |
| `requirements.txt` | Python deps (psutil) |

## Running
```powershell
# PowerShell — no install needed
.\Get-WindowsSystemMonitor.ps1 -OpenBrowser

# Python — install deps first
pip install -r requirements.txt
python system_monitor.py --live
```

## Notes
- No admin rights required
- No internet connection needed
- Python live mode exposes metrics API at `http://localhost:8000/api/metrics`
