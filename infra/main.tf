data "aws_caller_identity" "current" {}

locals {
  service_name     = var.service_name
  lambda_image_uri = "${aws_ecr_repository.images.repository_url}:${var.lambda_image_tag}"
}

data "external" "lambda_image_presence" {
  program = [
    "bash",
    "${path.module}/../scripts/check-ecr-image.sh",
  ]

  query = {
    repository_url = aws_ecr_repository.images.repository_url
    image_tag      = var.lambda_image_tag
    aws_region     = var.aws_region
  }
}

data "aws_iam_policy_document" "github_oidc_assume_role" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = [var.github_oidc_audience]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values = var.github_environment != "" ? [
        "repo:${var.github_owner}/${var.github_repo}:environment:${var.github_environment}"
        ] : [
        "repo:${var.github_owner}/${var.github_repo}:ref:refs/heads/${var.github_branch}"
      ]
    }
  }
}

data "aws_iam_policy_document" "github_actions_permissions" {
  statement {
    sid = "EcrPushPull"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:CompleteLayerUpload",
      "ecr:DescribeImages",
      "ecr:DescribeRepositories",
      "ecr:GetAuthorizationToken",
      "ecr:InitiateLayerUpload",
      "ecr:ListImages",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]
    resources = ["*"]
  }

  statement {
    sid = "ManageLambda"
    actions = [
      "lambda:GetFunction",
      "lambda:GetFunctionUrlConfig",
      "lambda:UpdateFunctionCode",
      "lambda:UpdateFunctionConfiguration",
    ]
    resources = ["*"]
  }

}

data "aws_iam_policy_document" "lambda_execution_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    var.github_oidc_audience,
  ]

  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
  ]
}

resource "aws_ecr_repository" "images" {
  name                 = local.service_name
  image_tag_mutability = var.image_tag_mutability

  image_scanning_configuration {
    scan_on_push = true
  }
}

data "aws_iam_policy_document" "lambda_ecr_repository" {
  statement {
    sid = "AllowLambdaPull"
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "aws:sourceArn"
      values = [
        "arn:aws:lambda:${var.aws_region}:${data.aws_caller_identity.current.account_id}:function:*",
      ]
    }
  }
}

resource "aws_ecr_repository_policy" "lambda_access" {
  repository = aws_ecr_repository.images.name
  policy     = data.aws_iam_policy_document.lambda_ecr_repository.json
}

resource "aws_iam_role" "lambda_execution" {
  name               = "${local.service_name}-lambda-execution"
  assume_role_policy = data.aws_iam_policy_document.lambda_execution_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "service" {
  count                        = data.external.lambda_image_presence.result.exists == "true" ? 1 : 0
  function_name                = local.service_name
  package_type                 = "Image"
  image_uri                    = local.lambda_image_uri
  role                         = aws_iam_role.lambda_execution.arn
  timeout                      = var.lambda_timeout
  memory_size                  = var.lambda_memory_size
  reserved_concurrent_executions = var.lambda_reserved_concurrency
  architectures                = ["x86_64"]

  lifecycle {
    ignore_changes = [image_uri]
  }
}

resource "aws_lambda_function_url" "service" {
  count              = data.external.lambda_image_presence.result.exists == "true" ? 1 : 0
  function_name      = aws_lambda_function.service[0].function_name
  authorization_type = "NONE"
}

resource "aws_lambda_permission" "function_url_invoke" {
  count                  = data.external.lambda_image_presence.result.exists == "true" ? 1 : 0
  statement_id           = "FunctionUrlPublicAccess"
  action                 = "lambda:InvokeFunctionUrl"
  function_name          = aws_lambda_function.service[0].function_name
  principal              = "*"
  function_url_auth_type = "NONE"
}

resource "aws_lambda_permission" "function_url_public_invoke" {
  count                    = data.external.lambda_image_presence.result.exists == "true" ? 1 : 0
  statement_id             = "FunctionUrlInvokePublicAccess"
  action                   = "lambda:InvokeFunction"
  function_name            = aws_lambda_function.service[0].function_name
  principal                = "*"
  invoked_via_function_url = true
}

resource "aws_iam_role" "github_actions" {
  name               = "${var.github_repo}-github-actions-deploy"
  assume_role_policy = data.aws_iam_policy_document.github_oidc_assume_role.json
}

resource "aws_iam_role_policy" "github_actions" {
  name   = "${var.github_repo}-github-actions-deploy"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_permissions.json
}
