# Quickstart Setup Guide Template

Use this template to create a step-by-step setup guide for developers or users getting started with a project.

---

# Quickstart — [Project Name]

**Time to first success**: ~[X minutes]  
**Target audience**: [Developers | End users | Data scientists | Teachers | etc.]  
**Prerequisites**: [Python 3.11+ | Node 18+ | AWS account | etc.]

## What You'll Build

[One paragraph describing what the user will have running by the end of this guide.]

**Example**: "You'll set up a Streamlit dashboard that visualizes your personal Garmin fitness data with AI-powered insights."

---

## Option A: [Quickest Path - 5 min]

For experienced developers who just want something running.

```bash
# 1. Clone and setup
cd [project-directory]
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Add your API key to .env

# 3. Run
python app.py
# or
streamlit run app.py
```

**Next step**: Jump to [Feature X] section, or see full [README.md](README.md)

---

## Option B: [Detailed Setup - 15-20 min]

For first-time setup or if you hit errors.

### 1️⃣ Prerequisites Check

```bash
# Check Python version
python --version
# Expected: Python 3.11 or higher

# Check Node (if needed)
node --version
# Expected: Node 18 or higher
```

If not installed, see [System Setup](#system-setup) section below.

### 2️⃣ Clone the Repository

```bash
git clone [repository-url]
cd [project-name]
```

### 3️⃣ Create Virtual Environment

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 4️⃣ Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Troubleshooting**:
- If pip fails: `python -m pip install --upgrade setuptools wheel`
- If a specific package fails: Check section [Common Issues](#common-issues) below

### 5️⃣ Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit with your secrets
nano .env
# or
code .env
```

**Required settings:**
- `API_KEY`: Your [Service] API key (get from [portal](link))
- `ENVIRONMENT`: Set to `development` for local work

**Optional settings:**
- `DEBUG`: Set to `true` for verbose logging
- `LOG_LEVEL`: `DEBUG` | `INFO` | `WARNING`

### 6️⃣ Verify Installation

```bash
# Run health check
python -m src.health_check

# Expected output:
# ✅ Database connection: OK
# ✅ API key configured: OK
# ✅ Dependencies: OK
```

### 7️⃣ Start the Application

```bash
# Option 1: Web app
streamlit run app.py
# Opens in browser: http://localhost:8501

# Option 2: CLI tool
python -m src.cli

# Option 3: API server
python -m src.api.main
# Runs on http://localhost:8000
```

✅ **You're running!** See [First Steps](#first-steps) below.

---

## First Steps

Now that you have the app running:

### Try Feature X
[Screenshot or example of feature X]

```bash
# Example command or UI interaction
```

### Load Sample Data
[How to load or create test data]

```bash
python scripts/load_sample_data.py
```

### Run Tests
```bash
pytest tests/ -v
```

---

## System Setup

### Install Python 3.11+

**macOS:**
```bash
brew install python@3.11
# Link it
brew link python@3.11 --force
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Run installer, check "Add Python to PATH"
- Verify: `python --version`

### Install Node (if needed)

**macOS:**
```bash
brew install node
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows:**
- Download from [nodejs.org](https://nodejs.org/)
- Run installer
- Verify: `node --version`

---

## Common Issues

### Issue: `ModuleNotFoundError: No module named '[package]'`

**Cause**: Virtual environment not activated or dependencies not installed

**Fix:**
```bash
# Verify venv is active (should see (.venv) in prompt)
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: `PermissionError: [Errno 13] Permission denied`

**Cause**: Trying to write to protected directory or file permissions issue

**Fix:**
```bash
# Fix file permissions
chmod +x scripts/*.sh

# Or use sudo (not recommended for development)
sudo chown -R $USER .
```

### Issue: `ImportError: cannot import name '[module]' from '[package]'`

**Cause**: Version mismatch or incomplete installation

**Fix:**
```bash
# Clean install
pip uninstall -y -r requirements.txt
pip install -r requirements.txt

# Or update pip
pip install --upgrade pip setuptools wheel
```

### Issue: `ConnectionError: Failed to connect to [service]`

**Cause**: Missing API key, wrong endpoint, or service down

**Fix:**
```bash
# Verify .env has correct API_KEY
cat .env | grep API_KEY

# Test connectivity
python scripts/test_connection.py
```

### Issue: Port already in use (e.g., `OSError: [Errno 48] Address already in use`)

**Cause**: Another instance is running on the same port

**Fix:**
```bash
# Find and kill process on port 8501 (example)
lsof -ti:8501 | xargs kill -9  # macOS/Linux

# Or use different port
streamlit run app.py --server.port 8502
```

---

## Next Steps

- 📖 **Full Documentation**: See [README.md](README.md)
- 🛠 **Development Setup**: See [CLAUDE.md](CLAUDE.md) for build/test commands
- 🔧 **Configuration**: All settings in [CLAUDE.md](CLAUDE.md#configuration)
- 📚 **API Reference**: See [API.md](docs/API.md) (if available)
- 🧪 **Running Tests**: `pytest tests/ -v`
- 🚀 **Deployment**: See [DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## Getting Help

- **Found a bug?** [Create an issue](link-to-issues)
- **Have a question?** Check [FAQ](FAQ.md) or open a discussion
- **Need to report a problem?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Last updated**: 2026-04-13  
**Tested on**: [Python 3.11 | macOS 14 | Ubuntu 22.04 | Windows 11]
