# AWS Secrets Manager for Garmin API Credentials

# Secret for Garmin OAuth credentials
resource "aws_secretsmanager_secret" "garmin_credentials" {
  name        = "${var.project_name}-garmin-credentials-${var.environment}"
  description = "Garmin Health API OAuth credentials (consumer key and secret)"

  recovery_window_in_days = 7

  tags = local.common_tags
}

# Store the secret value
resource "aws_secretsmanager_secret_version" "garmin_credentials_version" {
  secret_id = aws_secretsmanager_secret.garmin_credentials.id

  secret_string = jsonencode({
    consumer_key    = var.garmin_consumer_key
    consumer_secret = var.garmin_consumer_secret
  })
}

# Output
output "garmin_credentials_secret_name" {
  description = "Name of the Secrets Manager secret for Garmin credentials"
  value       = aws_secretsmanager_secret.garmin_credentials.name
}

output "garmin_credentials_secret_arn" {
  description = "ARN of the Secrets Manager secret for Garmin credentials"
  value       = aws_secretsmanager_secret.garmin_credentials.arn
  sensitive   = true
}
