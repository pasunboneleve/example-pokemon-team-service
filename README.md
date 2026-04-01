Example Pokemon Team Service
============================

Live URL
--------

- Lambda Function URL: `TODO`
- Optional local frontend: `frontend/index.html`

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

Run the local HTTP wrapper:

```bash
python3 -m pokemon_service.local_server
```

Then call the endpoint:

```bash
curl "http://127.0.0.1:8000/pokemon/team?names=pikachu,charizard,bulbasaur"
```

Run the test suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

If you want to open the tiny frontend, serve the repo root:

```bash
python3 -m http.server 4173
```

Then visit `http://127.0.0.1:4173/frontend/`.

Deployment
----------

The deployment flow is intentionally close to the template:

1. Copy `.env.template` to `.env` and load it with `direnv allow`
2. Create the Terraform state bucket with `./scripts/bootstrap-tf-state.sh`
3. Copy `infra/prod.tfvars.template` to `infra/prod.tfvars`
4. Initialize Terraform/OpenTofu in `infra/`
5. Apply Terraform/OpenTofu
6. Push to `main`

GitHub Actions will:

- assume the AWS deploy role through GitHub OIDC
- build the Lambda container image
- push the image to ECR
- create or update the Lambda function
- create or update the public Lambda Function URL

If the S3 backend refuses to use your AWS CLI profile during `tofu init`,
see the troubleshooting note in [`infra/INFRA.md`](infra/INFRA.md).

Structure
---------

- `pokemon_service/`
  Python application code and Lambda handler
- `tests/`
  unit tests for record transformation and team summary logic
- `frontend/`
  tiny static UI for manual checks
- `.github/workflows/deploy.yml`
  CI/CD workflow derived from the template, adapted for Lambda
- `infra/`
  Terraform for GitHub OIDC, ECR, Lambda execution IAM, and GitHub Actions secrets and variables
- `scripts/bootstrap-tf-state.sh`
  S3 remote state bootstrap, copied from the template
- `PLAN.md`
  short scope statement for this example adaptation

Template link
-------------

This service was built directly from
[`minimal-aws-github-ci-template`](https://github.com/pasunboneleve/aws-service-delivery-template).
