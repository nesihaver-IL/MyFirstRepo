#!/bin/bash
# Garmin Health Analytics Dashboard Quick-Start Script
# Run from project root: ./run.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANALYTICS_DIR="$PROJECT_DIR/analytics"
VENV_DIR="$ANALYTICS_DIR/.venv"

echo "=========================================="
echo "Garmin Health Analytics Dashboard"
echo "=========================================="
echo ""

# Step 1: Create or verify venv
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/4] Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "[1/4] Virtual environment already exists"
fi

# Step 2: Activate venv and upgrade pip
echo "[2/4] Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install -q --upgrade pip
pip install -q -r "$ANALYTICS_DIR/requirements.txt"

# Step 3: Verify .env file
if [ ! -f "$ANALYTICS_DIR/.env" ]; then
    echo "[3/4] Creating .env file (add ANTHROPIC_API_KEY manually if needed)"
    cat > "$ANALYTICS_DIR/.env" << 'EOF'
# Add your Anthropic API key here
ANTHROPIC_API_KEY=sk-ant-your-key-here
EOF
else
    echo "[3/4] .env file exists"
fi

# Step 4: Launch dashboard
echo "[4/4] Launching Streamlit dashboard..."
echo ""
echo "Dashboard will open at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

cd "$ANALYTICS_DIR"
streamlit run app.py
