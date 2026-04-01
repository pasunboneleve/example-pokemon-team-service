Pokemon Team Service Plan
=========================

What was copied directly from the template
------------------------------------------

- top-level repo shape: `infra/`, `scripts/`, `.github/workflows/`, `.env.template`, `AGENTS.md`
- Terraform/OpenTofu backend bootstrap and GitHub OIDC deployment approach
- GitHub Actions driven deployment flow from `main`
- repository conventions around `bd`, `direnv`, and Terraform-managed CI configuration
- remote state bootstrap through `scripts/bootstrap-tf-state.sh`

What was added for the Pokemon app
----------------------------------

- Python AWS Lambda application code for `GET /pokemon/team`
- Lambda container deployment instead of App Runner, while keeping ECR-based delivery
- Lambda Function URL infrastructure and deployment wiring
- small test suite for transformation and summary logic
- tiny optional static frontend for manual verification
- app-specific README content and local run instructions

What is intentionally out of scope
----------------------------------

- authentication, authorization, and rate limiting
- persistence, caching, and background jobs
- API Gateway, VPC, database, or queue infrastructure
- advanced frontend work
- broader Pokemon API coverage beyond the requested fields and summary
