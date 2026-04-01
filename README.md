Example Pokemon Team Service
============================

Live URL
--------

<!-- LIVE_URL_START -->
- Lambda Function URL: [Live URL](https://oz5d42va2dsixglkqcwewzq36e0adhmz.lambda-url.ap-southeast-2.on.aws/)
<!-- LIVE_URL_END -->
- Root URL serves a tiny frontend and calls `/pokemon/team`

## What this repo is

This is a deliberately small example service built by copying
`minimal-aws-github-ci-template` and changing only what was required
to ship a real AWS Lambda application.

The problem domain (Pokémon) is incidental.
This repository exists to validate that a minimal AWS delivery template
can take a trivial backend idea and make it publicly accessible with a
clean deployment path.

The public Lambda Function URL is intentionally capped with low reserved
concurrency by default so a stray script cannot scale the function
without bound. Adjust `lambda_reserved_concurrency` in
`infra/prod.tfvars` if you want a different cost/performance tradeoff.

## API

* `GET /pokemon/team?names=pikachu,charizard,bulbasaur`

The `names` parameter is a comma-separated list.
Pokémon may appear more than once.

For each Pokémon, the service returns:

* name
* height
* weight
* types
* stats (`hp`, `attack`, `defense`)
* image

The response also includes a team summary:

* `total_weight`
* `average_height`
* `total_hp`
* `type_counts`

Data source: [PokeAPI](https://pokeapi.co/)

## Error handling

Unknown Pokémon policy:

* if any requested name is unknown, the service returns `404`
* the response includes `unknown_names`
* partial teams are not returned

## Local run

Install the local Python environment with `uv`:

```bash
cd python
uv sync --group dev
```

Run the local service:

```bash
uv run pokemon-local
```

Open:

```
http://127.0.0.1:8000/
```

The root URL serves the frontend, which calls the local API.

Call the API directly:

```bash
curl "http://127.0.0.1:8000/pokemon/team?names=pikachu,charizard,bulbasaur"
```

Run tests:

```bash
cd python
uv run pytest
```

Watch tests:

```bash
cd python
uv run ptw
```

Refresh the README live URL block from Terraform state:

```bash
./scripts/update-readme-live-url.sh
```

## Deployment

The deployment flow stays intentionally close to the template:

1. Copy `.env.template` to `.env` and load it with `direnv allow`
2. Create the Terraform state bucket:

   ```bash
   ./scripts/bootstrap-tf-state.sh
   ```
3. Copy `infra/prod.tfvars.template` to `infra/prod.tfvars`
4. Initialize OpenTofu in `infra/`
5. Apply OpenTofu to create ECR, IAM roles, and GitHub configuration
6. Push to `main` so GitHub Actions publishes the first image to ECR
7. Apply OpenTofu again to create the Lambda function and Function URL
8. Run:

   ```bash
   ./scripts/update-readme-live-url.sh
   ```

With `direnv` loaded, `tofu plan`, `tofu apply`, `tofu destroy`, and `tofu import`
automatically use `infra/prod.tfvars`.

If `AWS_PROFILE` is set, `direnv reload` also refreshes AWS session credentials via
`aws configure export-credentials`.

GitHub Actions will:

* assume the AWS deploy role via GitHub OIDC
* build the Lambda container image
* push the image to ECR
* update the Terraform-managed Lambda function

Notes:

* If the S3 backend refuses your AWS CLI profile during `tofu init`,
  see [`infra/INFRA.md`](infra/INFRA.md)
* If `tofu output -raw function_url` is empty after the first apply,
  push once to create the initial image, then re-run `tofu apply`

## Structure

* `python/`
  Lambda handler, project metadata, and pytest suite
* `frontend/`
  tiny static UI served at `/`
* `.github/workflows/deploy.yml`
  CI/CD derived from the template, adapted for Lambda updates
* `infra/`
  OpenTofu for OIDC, ECR, Lambda, Function URL, and GitHub config
* `scripts/bootstrap-tf-state.sh`
  S3 remote state bootstrap (from template)
* `scripts/update-readme-live-url.sh`
  updates the README live URL section from `tofu output`
* `PLAN.md`
  scope and adaptation notes

## Template link

https://github.com/pasunboneleve/aws-service-delivery-template
