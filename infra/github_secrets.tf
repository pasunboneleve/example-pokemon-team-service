resource "github_actions_secret" "aws_role_to_assume" {
  repository      = var.github_repo
  secret_name     = "AWS_ROLE_TO_ASSUME"
  plaintext_value = aws_iam_role.github_actions.arn
}

resource "github_actions_variable" "aws_region" {
  repository    = var.github_repo
  variable_name = "AWS_REGION"
  value         = var.aws_region
}

resource "github_actions_variable" "aws_ecr_repository" {
  repository    = var.github_repo
  variable_name = "AWS_ECR_REPOSITORY"
  value         = aws_ecr_repository.images.name
}

resource "github_actions_variable" "aws_lambda_function_name" {
  repository    = var.github_repo
  variable_name = "AWS_LAMBDA_FUNCTION_NAME"
  value         = var.service_name
}

resource "github_actions_variable" "aws_lambda_memory_size" {
  repository    = var.github_repo
  variable_name = "AWS_LAMBDA_MEMORY_SIZE"
  value         = tostring(var.lambda_memory_size)
}

resource "github_actions_variable" "aws_lambda_timeout" {
  repository    = var.github_repo
  variable_name = "AWS_LAMBDA_TIMEOUT"
  value         = tostring(var.lambda_timeout)
}
