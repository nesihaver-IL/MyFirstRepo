# Lambda Functions for Garmin Integration

# Package Lambda functions
data "archive_file" "webhook_handler" {
  type        = "zip"
  source_file = "${path.module}/../lambda/garmin_webhook_handler.py"
  output_path = "${path.module}/lambda_packages/webhook_handler.zip"
}

data "archive_file" "fetch_activity" {
  type        = "zip"
  source_file = "${path.module}/../lambda/garmin_fetch_activity.py"
  output_path = "${path.module}/lambda_packages/fetch_activity.zip"
}

data "archive_file" "ai_analyzer" {
  type        = "zip"
  source_file = "${path.module}/../lambda/garmin_ai_analyzer.py"
  output_path = "${path.module}/lambda_packages/ai_analyzer.zip"
}

data "archive_file" "oauth_handler" {
  type        = "zip"
  source_file = "${path.module}/../lambda/garmin_oauth_handler.py"
  output_path = "${path.module}/lambda_packages/oauth_handler.zip"
}

# Lambda Layer for dependencies (requests, requests-oauthlib, boto3)
resource "aws_lambda_layer_version" "garmin_dependencies" {
  filename            = "${path.module}/lambda_packages/dependencies_layer.zip"
  layer_name          = "${var.project_name}-dependencies-${var.environment}"
  compatible_runtimes = ["python3.11", "python3.12"]
  description         = "Dependencies for Garmin integration (requests, requests-oauthlib)"

  # This file should be created by running: pip install -t python/lib/python3.11/site-packages requests requests-oauthlib
  # Then: zip -r dependencies_layer.zip python
}

# 1. Webhook Handler Lambda
resource "aws_lambda_function" "webhook_handler" {
  filename         = data.archive_file.webhook_handler.output_path
  function_name    = "${var.project_name}-webhook-handler-${var.environment}"
  role            = aws_iam_role.webhook_handler_role.arn
  handler         = "garmin_webhook_handler.lambda_handler"
  source_code_hash = data.archive_file.webhook_handler.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256

  environment {
    variables = {
      ACTIVITIES_TABLE_NAME = aws_dynamodb_table.garmin_activities.name
      EVENT_BUS_NAME        = "default"
      LOG_LEVEL             = "INFO"
    }
  }

  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Garmin Webhook Handler"
    }
  )
}

# CloudWatch Log Group for webhook handler
resource "aws_cloudwatch_log_group" "webhook_handler" {
  name              = "/aws/lambda/${aws_lambda_function.webhook_handler.function_name}"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

# 2. Fetch Activity Lambda
resource "aws_lambda_function" "fetch_activity" {
  filename         = data.archive_file.fetch_activity.output_path
  function_name    = "${var.project_name}-fetch-activity-${var.environment}"
  role            = aws_iam_role.fetch_activity_role.arn
  handler         = "garmin_fetch_activity.lambda_handler"
  source_code_hash = data.archive_file.fetch_activity.output_base64sha256
  runtime         = "python3.11"
  timeout         = 60
  memory_size     = 512
  layers          = [aws_lambda_layer_version.garmin_dependencies.arn]

  environment {
    variables = {
      TOKENS_TABLE_NAME           = aws_dynamodb_table.garmin_user_tokens.name
      ACTIVITIES_TABLE_NAME       = aws_dynamodb_table.garmin_activities.name
      GARMIN_CREDENTIALS_SECRET   = aws_secretsmanager_secret.garmin_credentials.name
      EVENT_BUS_NAME              = "default"
      LOG_LEVEL                   = "INFO"
    }
  }

  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Garmin Activity Fetcher"
    }
  )
}

# CloudWatch Log Group for fetch activity
resource "aws_cloudwatch_log_group" "fetch_activity" {
  name              = "/aws/lambda/${aws_lambda_function.fetch_activity.function_name}"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

# 3. AI Analyzer Lambda
resource "aws_lambda_function" "ai_analyzer" {
  filename         = data.archive_file.ai_analyzer.output_path
  function_name    = "${var.project_name}-ai-analyzer-${var.environment}"
  role            = aws_iam_role.ai_analyzer_role.arn
  handler         = "garmin_ai_analyzer.lambda_handler"
  source_code_hash = data.archive_file.ai_analyzer.output_base64sha256
  runtime         = "python3.11"
  timeout         = var.lambda_timeout
  memory_size     = var.lambda_memory_size

  environment {
    variables = {
      ACTIVITIES_TABLE_NAME  = aws_dynamodb_table.garmin_activities.name
      BEDROCK_AGENT_ID       = var.bedrock_agent_id
      BEDROCK_AGENT_ALIAS_ID = var.bedrock_agent_alias_id
      BEDROCK_MODEL_ID       = var.bedrock_model_id
      LOG_LEVEL              = "INFO"
    }
  }

  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Garmin AI Analyzer"
    }
  )
}

# CloudWatch Log Group for AI analyzer
resource "aws_cloudwatch_log_group" "ai_analyzer" {
  name              = "/aws/lambda/${aws_lambda_function.ai_analyzer.function_name}"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

# 4. OAuth Handler Lambda
resource "aws_lambda_function" "oauth_handler" {
  filename         = data.archive_file.oauth_handler.output_path
  function_name    = "${var.project_name}-oauth-handler-${var.environment}"
  role            = aws_iam_role.oauth_handler_role.arn
  handler         = "garmin_oauth_handler.lambda_handler"
  source_code_hash = data.archive_file.oauth_handler.output_base64sha256
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 256
  layers          = [aws_lambda_layer_version.garmin_dependencies.arn]

  environment {
    variables = {
      TOKENS_TABLE_NAME           = aws_dynamodb_table.garmin_user_tokens.name
      GARMIN_CREDENTIALS_SECRET   = aws_secretsmanager_secret.garmin_credentials.name
      CALLBACK_URL                = "${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/oauth/callback"
      LOG_LEVEL                   = "INFO"
    }
  }

  tracing_config {
    mode = var.enable_xray_tracing ? "Active" : "PassThrough"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Garmin OAuth Handler"
    }
  )
}

# CloudWatch Log Group for OAuth handler
resource "aws_cloudwatch_log_group" "oauth_handler" {
  name              = "/aws/lambda/${aws_lambda_function.oauth_handler.function_name}"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

# Outputs
output "webhook_handler_function_name" {
  description = "Name of the webhook handler Lambda function"
  value       = aws_lambda_function.webhook_handler.function_name
}

output "webhook_handler_function_arn" {
  description = "ARN of the webhook handler Lambda function"
  value       = aws_lambda_function.webhook_handler.arn
}

output "fetch_activity_function_name" {
  description = "Name of the fetch activity Lambda function"
  value       = aws_lambda_function.fetch_activity.function_name
}

output "ai_analyzer_function_name" {
  description = "Name of the AI analyzer Lambda function"
  value       = aws_lambda_function.ai_analyzer.function_name
}

output "oauth_handler_function_name" {
  description = "Name of the OAuth handler Lambda function"
  value       = aws_lambda_function.oauth_handler.function_name
}
