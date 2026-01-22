#!/bin/bash
# Destroy Garmin Integration Infrastructure

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
log_warn "WARNING: This will destroy all Garmin Integration infrastructure!"
log_warn "This includes:"
log_warn "  - All Lambda functions"
log_warn "  - DynamoDB tables (all activity data will be lost)"
log_warn "  - API Gateway"
log_warn "  - EventBridge rules"
log_warn "  - Secrets Manager secrets"
echo ""

read -p "Are you absolutely sure you want to destroy everything? (type 'destroy' to confirm): " confirm

if [ "$confirm" = "destroy" ]; then
    cd "$TERRAFORM_DIR"
    terraform destroy
    echo ""
    log_warn "Infrastructure destroyed."
else
    log_warn "Destruction cancelled."
    exit 0
fi
