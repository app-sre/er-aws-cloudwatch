# External Resources Cloudwatch Module

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

External Resources module to provision and manage CloudWatch log groups in AWS with app-interface.

## Tech stack

* Terraform
* AWS provider
* Python 3.12
* Pydantic

## Development

Prepare your local development environment:

```bash
make dev
```

See the `Makefile` for more details.

### Update Terraform modules

To update the Terraform modules used in this project, bump the version in [versions.tf](/terraform/versions.tf) and update the Terraform lockfile via:

```bash
make providers-lock
```

### Development workflow

1. Make changes to the code.
1. Update the `vars.tf` file after `app_interface_input.py` changes via `make generate-variables-tf`.
1. Build the image with `make build`.
1. Run the image manually with a proper input file and credentials.
