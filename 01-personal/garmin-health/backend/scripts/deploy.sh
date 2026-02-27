#!/bin/bash
# Main Deployment Script for Garmin Integration

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
LAMBDA_DIR="$PROJECT_ROOT/lambda"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform not found. Please install Terraform."
        exit 1
    fi

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI."
        exit 1
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3."
        exit 1
    fi

    log_info "All prerequisites met."
}

# Build Lambda layer
build_lambda_layer() {
    log_info "Building Lambda layer..."

    mkdir -p "$TERRAFORM_DIR/lambda_packages"
    cd "$TERRAFORM_DIR/lambda_packages"

    # Create temporary directory for layer
    rm -rf python
    mkdir -p python/lib/python3.11/site-packages

    # Install dependencies
    log_info "Installing Python dependencies..."
    pip3 install -t python/lib/python3.11/site-packages \
        -r "$LAMBDA_DIR/requirements.txt" \
        --platform manylinux2014_x86_64 \
        --only-binary=:all: \
        --upgrade

    # Create zip
    log_info "Creating layer zip file..."
    zip -r dependencies_layer.zip python > /dev/null

    # Cleanup
    rm -rf python

    log_info "Lambda layer built successfully."
}

# Initialize Terraform
init_terraform() {
    log_info "Initializing Terraform..."
    cd "$TERRAFORM_DIR"
    terraform init
    log_info "Terraform initialized."
}

# Validate Terraform configuration
validate_terraform() {
    log_info "Validating Terraform configuration..."
    cd "$TERRAFORM_DIR"
    terraform validate
    log_info "Terraform configuration is valid."
}

# Plan Terraform deployment
plan_terraform() {
    log_info "Planning Terraform deployment..."
    cd "$TERRAFORM_DIR"
    terraform plan -out=tfplan
    log_info "Terraform plan created."
}

# Apply Terraform deployment
apply_terraform() {
    log_info "Applying Terraform deployment..."
    cd "$TERRAFORM_DIR"
    terraform apply tfplan
    log_info "Terraform deployment complete."
}

# Display outputs
display_outputs() {
    log_info "Retrieving deployment outputs..."
    cd "$TERRAFORM_DIR"
    terraform output
}

# Main deployment flow
main() {
    log_info "Starting Garmin Integration deployment..."

    check_prerequisites

    # Check if terraform.tfvars exists
    if [ ! -f "$TERRAFORM_DIR/terraform.tfvars" ]; then
        log_error "terraform.tfvars not found!"
        log_warn "Please copy config/terraform.tfvars.example to terraform/terraform.tfvars and configure it."
        exit 1
    fi

    build_lambda_layer
    init_terraform
    validate_terraform
    plan_terraform

    # Ask for confirmation
    echo ""
    read -p "Do you want to apply this deployment? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        apply_terraform
        echo ""
        log_info "Deployment completed successfully!"
        echo ""
        display_outputs
    else
        log_warn "Deployment cancelled."
        exit 0
    fi
}

# Run main function
main "$@"
