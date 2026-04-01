variable "aws_region" {
  description = "AWS region used for ECR, Lambda, and Terraform state."
  type        = string
}

variable "service_name" {
  description = "Base service name used for the ECR repository and Lambda function."
  type        = string
}

variable "github_owner" {
  description = "GitHub organization or user."
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name."
  type        = string
}

variable "github_branch" {
  description = "Git ref allowed to assume the GitHub Actions deploy role."
  type        = string
  default     = "main"
}

variable "github_oidc_audience" {
  description = "Audience used by GitHub's OIDC token when assuming the AWS role."
  type        = string
  default     = "sts.amazonaws.com"
}

variable "github_environment" {
  description = "Optional GitHub Actions environment name to constrain the OIDC trust policy."
  type        = string
  default     = ""
}

variable "github_repo_visibility" {
  description = "Metadata tag only. Useful when publishing the template."
  type        = string
  default     = "private"
}

variable "github_token" {
  description = "Optional GitHub Personal Access Token with repo scope for managing Actions secrets."
  type        = string
  sensitive   = true
  default     = null
}

variable "image_tag_mutability" {
  description = "ECR tag mutability setting."
  type        = string
  default     = "MUTABLE"
}

variable "lambda_memory_size" {
  description = "Lambda memory size in MB."
  type        = number
  default     = 256
}

variable "lambda_timeout" {
  description = "Lambda timeout in seconds."
  type        = number
  default     = 15
}

variable "lambda_reserved_concurrency" {
  description = "Hard cap on concurrent Lambda executions to limit cost exposure for the public Function URL."
  type        = number
  default     = 5
}

variable "lambda_image_tag" {
  description = "Container image tag Terraform should use when creating or recreating the Lambda function."
  type        = string
  default     = "latest"
}
