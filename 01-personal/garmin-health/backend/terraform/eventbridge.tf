# EventBridge Rules for Orchestrating Garmin Integration

# ==================== New Activity Event Rule ====================

# Rule to trigger activity fetcher when new activity webhook is received
resource "aws_cloudwatch_event_rule" "new_activity" {
  name        = "${var.project_name}-new-activity-${var.environment}"
  description = "Triggered when new Garmin activity webhook is received"

  event_pattern = jsonencode({
    source      = ["garmin.webhook"]
    detail-type = ["NewActivityReceived"]
  })

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "new_activity_target" {
  rule      = aws_cloudwatch_event_rule.new_activity.name
  target_id = "FetchActivityLambda"
  arn       = aws_lambda_function.fetch_activity.arn
  role_arn  = aws_iam_role.eventbridge_role.arn
}

# Lambda permission for EventBridge to invoke fetch_activity
resource "aws_lambda_permission" "new_activity_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fetch_activity.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.new_activity.arn
}

# ==================== Activity Data Ready Event Rule ====================

# Rule to trigger AI analyzer when activity data is fetched
resource "aws_cloudwatch_event_rule" "activity_data_ready" {
  name        = "${var.project_name}-activity-data-ready-${var.environment}"
  description = "Triggered when activity data is fetched and ready for AI analysis"

  event_pattern = jsonencode({
    source      = ["garmin.activity-fetcher"]
    detail-type = ["ActivityDataReady"]
  })

  tags = local.common_tags
}

resource "aws_cloudwatch_event_target" "activity_data_ready_target" {
  rule      = aws_cloudwatch_event_rule.activity_data_ready.name
  target_id = "AIAnalyzerLambda"
  arn       = aws_lambda_function.ai_analyzer.arn
  role_arn  = aws_iam_role.eventbridge_role.arn
}

# Lambda permission for EventBridge to invoke ai_analyzer
resource "aws_lambda_permission" "activity_data_ready_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ai_analyzer.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.activity_data_ready.arn
}

# ==================== Dead Letter Queue (DLQ) ====================

# SQS DLQ for failed EventBridge events
resource "aws_sqs_queue" "eventbridge_dlq" {
  name                      = "${var.project_name}-eventbridge-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days

  tags = local.common_tags
}

# SQS Queue Policy
resource "aws_sqs_queue_policy" "eventbridge_dlq_policy" {
  queue_url = aws_sqs_queue.eventbridge_dlq.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.eventbridge_dlq.arn
      }
    ]
  })
}

# ==================== CloudWatch Alarms for EventBridge ====================

# Alarm for failed event deliveries
resource "aws_cloudwatch_metric_alarm" "eventbridge_failed_invocations" {
  alarm_name          = "${var.project_name}-eventbridge-failed-invocations-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "FailedInvocations"
  namespace           = "AWS/Events"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "Alert when EventBridge has more than 5 failed invocations"
  treat_missing_data  = "notBreaching"

  dimensions = {
    RuleName = aws_cloudwatch_event_rule.new_activity.name
  }

  tags = local.common_tags
}

# Outputs
output "new_activity_rule_name" {
  description = "Name of the new activity EventBridge rule"
  value       = aws_cloudwatch_event_rule.new_activity.name
}

output "activity_data_ready_rule_name" {
  description = "Name of the activity data ready EventBridge rule"
  value       = aws_cloudwatch_event_rule.activity_data_ready.name
}

output "eventbridge_dlq_url" {
  description = "URL of the EventBridge Dead Letter Queue"
  value       = aws_sqs_queue.eventbridge_dlq.url
}
