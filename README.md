Example Pokemon Team Service
============================

Live URL
--------

<!-- LIVE_URL_START -->
- Lambda Function URL: `https://oz5d42va2dsixglkqcwewzq36e0adhmz.lambda-url.ap-southeast-2.on.aws/`
<!-- LIVE_URL_END -->
- Root URL serves the tiny frontend and calls `/pokemon/team` from the page

What this repo is
-----------------

This repository is a deliberately small example application created by
starting from `minimal-aws-github-ci-template` and changing only what
was necessary to ship a real AWS Lambda service.

It exposes:

- `GET /pokemon/team?names=pikachu,charizard,bulbasaur`

For each requested Pokemon it returns:

- name
- height
- weight
- types
- stats including `hp`, `attack`, and `defense`
- image

It also returns a team summary with:

- `total_weight`
- `average_height`
- `total_hp`
- `type_counts`

The upstream data source is [PokeAPI](https://pokeapi.co/).

Unknown Pokemon policy:

- if any requested name is unknown, the service returns `404`
- the response includes `unknown_names`
- the service does not return a partial team

Local run
---------

Install the local Python environment with `uv`:

```bash
cd python
uv sync --group dev
```

Run the local service:

```bash
uv run pokemon-local
```

Then open `http://127.0.0.1:8000/`.
The root URL serves the tiny frontend, and the frontend calls the local API endpoint.

If you want to hit the API directly:

```bash
curl "http://127.0.0.1:8000/pokemon/team?names=pikachu,charizard,bulbasaur"
```

Run the test suite:

```bash
cd python
uv run pytest
```

Watch tests locally while editing:

```bash
cd python
uv run ptw
```

Refresh the README live URL block from Terraform state:

```bash
./scripts/update-readme-live-url.sh
```

Deployment
----------

The deployment flow is intentionally close to the template:

1. Copy `.env.template` to `.env` and load it with `direnv allow`
2. Create the Terraform state bucket with `./scripts/bootstrap-tf-state.sh`
3. Copy `infra/prod.tfvars.template` to `infra/prod.tfvars`
4. Initialize Terraform/OpenTofu in `infra/`
5. Apply Terraform/OpenTofu to create the ECR repository, IAM roles, and GitHub Actions configuration
6. Push to `main` once so GitHub Actions publishes the first `latest` image to ECR
7. Apply Terraform/OpenTofu again so it can create the Lambda function and Function URL from that image
8. Run `./scripts/update-readme-live-url.sh`

With `direnv` loaded, `tofu plan`, `tofu apply`, `tofu destroy`, and `tofu import`
automatically use `infra/prod.tfvars`.
If `AWS_PROFILE` is set, `direnv reload` also refreshes exported AWS
session credentials using `aws configure export-credentials`.

GitHub Actions will:

- assume the AWS deploy role through GitHub OIDC
- build the Lambda container image
- push the image to ECR
- update the existing Terraform-managed Lambda function

If the S3 backend refuses to use your AWS CLI profile during `tofu init`,
see the troubleshooting note in [`infra/INFRA.md`](infra/INFRA.md).
If `tofu output -raw function_url` is still empty after the first apply,
that just means the bootstrap image does not exist in ECR yet. Push once,
then rerun `tofu apply`.

Structure
---------

- `python/`
  Python project metadata, Lambda handler package, and pytest suite
- `frontend/`
  tiny static UI served at `/`
- `.github/workflows/deploy.yml`
  CI/CD workflow derived from the template, adapted for Lambda code updates
- `infra/`
  Terraform for GitHub OIDC, ECR, Lambda, Function URL, and GitHub Actions secrets and variables
- `scripts/bootstrap-tf-state.sh`
  S3 remote state bootstrap, copied from the template
- `scripts/update-readme-live-url.sh`
  updates the README live URL section from `tofu output`
- `PLAN.md`
  short scope statement for this example adaptation

Template link
-------------

This service was built directly from
[`minimal-aws-github-ci-template`](https://github.com/pasunboneleve/aws-service-delivery-template).
