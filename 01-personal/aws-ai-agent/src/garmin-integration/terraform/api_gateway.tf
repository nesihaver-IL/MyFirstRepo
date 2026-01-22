# API Gateway for Garmin Integration

# REST API
resource "aws_api_gateway_rest_api" "garmin_api" {
  name        = "${var.project_name}-api-${var.environment}"
  description = "API Gateway for Garmin Connect integration"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = local.common_tags
}

# ==================== Webhook Endpoint ====================

# /webhook resource
resource "aws_api_gateway_resource" "webhook" {
  rest_api_id = aws_api_gateway_rest_api.garmin_api.id
  parent_id   = aws_api_gateway_rest_api.garmin_api.root_resource_id
  path_part   = "webhook"
}

# POST /webhook
resource "aws_api_gateway_method" "webhook_post" {
  rest_api_id   = aws_api_gateway_rest_api.garmin_api.id
  resource_id   = aws_api_gateway_resource.webhook.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "webhook_integration" {
  rest_api_id             = aws_api_gateway_rest_api.garmin_api.id
  resource_id             = aws_api_gateway_resource.webhook.id
  http_method             = aws_api_gateway_method.webhook_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.webhook_handler.invoke_arn
}

# Lambda permission for webhook
resource "aws_lambda_permission" "webhook_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.webhook_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.garmin_api.execution_arn}/*/*"
}

# ==================== OAuth Endpoints ====================

# /oauth resource
resource "aws_api_gateway_resource" "oauth" {
  rest_api_id = aws_api_gateway_rest_api.garmin_api.id
  parent_id   = aws_api_gateway_rest_api.garmin_api.root_resource_id
  path_part   = "oauth"
}

# /oauth/initiate resource
resource "aws_api_gateway_resource" "oauth_initiate" {
  rest_api_id = aws_api_gateway_rest_api.garmin_api.id
  parent_id   = aws_api_gateway_resource.oauth.id
  path_part   = "initiate"
}

# POST /oauth/initiate
resource "aws_api_gateway_method" "oauth_initiate_post" {
  rest_api_id   = aws_api_gateway_rest_api.garmin_api.id
  resource_id   = aws_api_gateway_resource.oauth_initiate.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "oauth_initiate_integration" {
  rest_api_id             = aws_api_gateway_rest_api.garmin_api.id
  resource_id             = aws_api_gateway_resource.oauth_initiate.id
  http_method             = aws_api_gateway_method.oauth_initiate_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.oauth_handler.invoke_arn
}

# /oauth/callback resource
resource "aws_api_gateway_resource" "oauth_callback" {
  rest_api_id = aws_api_gateway_rest_api.garmin_api.id
  parent_id   = aws_api_gateway_resource.oauth.id
  path_part   = "callback"
}

# GET /oauth/callback
resource "aws_api_gateway_method" "oauth_callback_get" {
  rest_api_id   = aws_api_gateway_rest_api.garmin_api.id
  resource_id   = aws_api_gateway_resource.oauth_callback.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "oauth_callback_integration" {
  rest_api_id             = aws_api_gateway_rest_api.garmin_api.id
  resource_id             = aws_api_gateway_resource.oauth_callback.id
  http_method             = aws_api_gateway_method.oauth_callback_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.oauth_handler.invoke_arn
}

# Lambda permission for OAuth
resource "aws_lambda_permission" "oauth_api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.oauth_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.garmin_api.execution_arn}/*/*"
}

# ==================== Health Check Endpoint ====================

# /health resource
resource "aws_api_gateway_resource" "health" {
  rest_api_id = aws_api_gateway_rest_api.garmin_api.id
  parent_id   = aws_api_gateway_rest_api.garmin_api.root_resource_id
  path_part   = "health"
}

# GET /health (mock response)
resource "aws_api_gateway_method" "health_get" {
  rest_api_id   = aws_api_gateway_rest_api.garmin_api.id
  resource_id   = aws_api_gateway_resource.health.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "health_integration" {
  rest_api_id = aws_api_gateway_rest_api.garmin_api.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_get.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "health_response" {
  rest_api_id = aws_api_gateway_rest_api.garmin_api.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_get.http_method
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "health_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.garmin_api.id
  resource_id = aws_api_gateway_resource.health.id
  http_method = aws_api_gateway_method.health_get.http_method
  status_code = aws_api_gateway_method_response.health_response.status_code

  response_templates = {
    "application/json" = jsonencode({
      status  = "healthy"
      service = "garmin-integration"
    })
  }

  depends_on = [aws_api_gateway_integration.health_integration]
}

# ==================== API Deployment ====================

resource "aws_api_gateway_deployment" "garmin_api" {
  rest_api_id = aws_api_gateway_rest_api.garmin_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.webhook.id,
      aws_api_gateway_method.webhook_post.id,
      aws_api_gateway_integration.webhook_integration.id,
      aws_api_gateway_resource.oauth_initiate.id,
      aws_api_gateway_method.oauth_initiate_post.id,
      aws_api_gateway_resource.oauth_callback.id,
      aws_api_gateway_method.oauth_callback_get.id,
      aws_api_gateway_resource.health.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "garmin_api_stage" {
  deployment_id = aws_api_gateway_deployment.garmin_api.id
  rest_api_id   = aws_api_gateway_rest_api.garmin_api.id
  stage_name    = var.api_gateway_stage_name

  xray_tracing_enabled = var.enable_xray_tracing

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  tags = local.common_tags
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = local.common_tags
}

# Outputs
output "api_gateway_url" {
  description = "Base URL for API Gateway"
  value       = aws_api_gateway_deployment.garmin_api.invoke_url
}

output "webhook_endpoint" {
  description = "Full URL for Garmin webhook endpoint"
  value       = "${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/webhook"
}

output "oauth_initiate_endpoint" {
  description = "Full URL for OAuth initiation endpoint"
  value       = "${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/oauth/initiate"
}

output "oauth_callback_endpoint" {
  description = "Full URL for OAuth callback endpoint"
  value       = "${aws_api_gateway_deployment.garmin_api.invoke_url}/${var.api_gateway_stage_name}/oauth/callback"
}
