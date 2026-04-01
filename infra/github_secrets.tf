resource "github_actions_secret" "aws_role_to_assume" {
  repository      = var.github_repo
  secret_name     = "AWS_ROLE_TO_ASSUME"
  plaintext_value = aws_iam_role.github_actions.arn
}

resource "github_actions_secret" "aws_lambda_execution_role_arn" {
  repository      = var.github_repo
  secret_name     = "AWS_LAMBDA_EXECUTION_ROLE_ARN"
  plaintext_value = aws_iam_role.lambda_execution.arn
}
