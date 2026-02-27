# Terraform Outputs for Garmin Integration

# ==================== API Gateway Outputs ====================

output "api_gateway_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.garmin_api.id
}

output "api_gateway_stage_invoke_url" {
  description = "Invoke URL for the API Gateway stage"
  value       = "${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}"
}

# ==================== Endpoint URLs ====================

output "webhook_url" {
  description = "Webhook URL to register with Garmin Health API"
  value       = "${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/webhook"
}

output "oauth_initiate_url" {
  description = "URL to initiate OAuth flow"
  value       = "${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/oauth/initiate"
}

output "oauth_callback_url" {
  description = "OAuth callback URL for Garmin registration"
  value       = "${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/oauth/callback"
}

output "health_check_url" {
  description = "Health check endpoint URL"
  value       = "${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/health"
}

# ==================== Lambda Function Outputs ====================

output "lambda_functions" {
  description = "Map of Lambda function names and ARNs"
  value = {
    webhook_handler = {
      name = aws_lambda_function.webhook_handler.function_name
      arn  = aws_lambda_function.webhook_handler.arn
    }
    fetch_activity = {
      name = aws_lambda_function.fetch_activity.function_name
      arn  = aws_lambda_function.fetch_activity.arn
    }
    ai_analyzer = {
      name = aws_lambda_function.ai_analyzer.function_name
      arn  = aws_lambda_function.ai_analyzer.arn
    }
    oauth_handler = {
      name = aws_lambda_function.oauth_handler.function_name
      arn  = aws_lambda_function.oauth_handler.arn
    }
  }
}

# ==================== DynamoDB Outputs ====================

output "dynamodb_tables" {
  description = "Map of DynamoDB table names and ARNs"
  value = {
    activities = {
      name = aws_dynamodb_table.garmin_activities.name
      arn  = aws_dynamodb_table.garmin_activities.arn
    }
    user_tokens = {
      name = aws_dynamodb_table.garmin_user_tokens.name
      arn  = aws_dynamodb_table.garmin_user_tokens.arn
    }
  }
}

# ==================== EventBridge Outputs ====================

output "eventbridge_rules" {
  description = "Map of EventBridge rule names and ARNs"
  value = {
    new_activity = {
      name = aws_cloudwatch_event_rule.new_activity.name
      arn  = aws_cloudwatch_event_rule.new_activity.arn
    }
    activity_data_ready = {
      name = aws_cloudwatch_event_rule.activity_data_ready.name
      arn  = aws_cloudwatch_event_rule.activity_data_ready.arn
    }
  }
}

# ==================== Monitoring Outputs ====================

output "cloudwatch_log_groups" {
  description = "Map of CloudWatch Log Group names"
  value = {
    webhook_handler = aws_cloudwatch_log_group.webhook_handler.name
    fetch_activity  = aws_cloudwatch_log_group.fetch_activity.name
    ai_analyzer     = aws_cloudwatch_log_group.ai_analyzer.name
    oauth_handler   = aws_cloudwatch_log_group.oauth_handler.name
    api_gateway     = aws_cloudwatch_log_group.api_gateway_logs.name
  }
}

output "dlq_url" {
  description = "Dead Letter Queue URL for failed events"
  value       = aws_sqs_queue.eventbridge_dlq.url
}

# ==================== Setup Instructions ====================

output "setup_instructions" {
  description = "Instructions for completing the setup"
  value = <<-EOT

    ==================== Garmin Integration Setup ====================

    1. Register your webhook with Garmin Health API:
       Webhook URL: ${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/webhook

    2. OAuth Callback URL for Garmin Developer Console:
       Callback URL: ${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/oauth/callback

    3. Test OAuth flow:
       POST ${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/oauth/initiate
       Body: {"user_id": "test_user_123"}

    4. Health check:
       GET ${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/health

    5. Monitor CloudWatch Logs:
       - Webhook Handler: /aws/lambda/${aws_lambda_function.webhook_handler.function_name}
       - Fetch Activity: /aws/lambda/${aws_lambda_function.fetch_activity.function_name}
       - AI Analyzer: /aws/lambda/${aws_lambda_function.ai_analyzer.function_name}

    6. View DynamoDB Tables:
       - Activities: ${aws_dynamodb_table.garmin_activities.name}
       - User Tokens: ${aws_dynamodb_table.garmin_user_tokens.name}

    ================================================================
  EOT
}
