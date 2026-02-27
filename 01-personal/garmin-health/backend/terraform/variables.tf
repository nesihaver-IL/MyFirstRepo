# Terraform Variables for Garmin Integration

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name prefix for resources"
  type        = string
  default     = "garmin-integration"
}

variable "bedrock_agent_id" {
  description = "AWS Bedrock Agent ID (if using agent)"
  type        = string
  default     = ""
}

variable "bedrock_agent_alias_id" {
  description = "AWS Bedrock Agent Alias ID"
  type        = string
  default     = ""
}

variable "bedrock_model_id" {
  description = "Bedrock model ID for direct invocation (fallback)"
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}

variable "garmin_consumer_key" {
  description = "Garmin API Consumer Key (OAuth)"
  type        = string
  sensitive   = true
}

variable "garmin_consumer_secret" {
  description = "Garmin API Consumer Secret (OAuth)"
  type        = string
  sensitive   = true
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PROVISIONED or PAY_PER_REQUEST)"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "enable_xray_tracing" {
  description = "Enable AWS X-Ray tracing for Lambda functions"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention in days"
  type        = number
  default     = 30
}

variable "api_gateway_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "prod"
}
