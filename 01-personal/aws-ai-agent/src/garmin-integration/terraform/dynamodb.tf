# DynamoDB Tables for Garmin Integration

# Activities Table - Stores all Garmin activities and their analysis
resource "aws_dynamodb_table" "garmin_activities" {
  name           = "${var.project_name}-activities-${var.environment}"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "activity_id"

  attribute {
    name = "activity_id"
    type = "S"
  }

  attribute {
    name = "user_token"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  # Global Secondary Index for querying activities by user and time
  global_secondary_index {
    name            = "user-timestamp-index"
    hash_key        = "user_token"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  # TTL for automatic data cleanup (optional)
  ttl {
    enabled        = true
    attribute_name = "ttl"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Garmin Activities Table"
    }
  )
}

# User Tokens Table - Stores OAuth tokens for each user
resource "aws_dynamodb_table" "garmin_user_tokens" {
  name           = "${var.project_name}-user-tokens-${var.environment}"
  billing_mode   = var.dynamodb_billing_mode
  hash_key       = "user_token"

  attribute {
    name = "user_token"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  # Global Secondary Index for querying by user_id
  global_secondary_index {
    name            = "user-id-index"
    hash_key        = "user_id"
    projection_type = "ALL"
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  # TTL for temporary tokens (request tokens)
  ttl {
    enabled        = true
    attribute_name = "ttl"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "Garmin User Tokens Table"
    }
  )
}

# Outputs
output "activities_table_name" {
  description = "Name of the activities DynamoDB table"
  value       = aws_dynamodb_table.garmin_activities.name
}

output "activities_table_arn" {
  description = "ARN of the activities DynamoDB table"
  value       = aws_dynamodb_table.garmin_activities.arn
}

output "user_tokens_table_name" {
  description = "Name of the user tokens DynamoDB table"
  value       = aws_dynamodb_table.garmin_user_tokens.name
}

output "user_tokens_table_arn" {
  description = "ARN of the user tokens DynamoDB table"
  value       = aws_dynamodb_table.garmin_user_tokens.arn
}
