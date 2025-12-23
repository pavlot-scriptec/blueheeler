# Development
## Build
To validate and build project run:
`poetry run task build`

If it generate errors you can try to fix them running:
`poetry run ruff check --fix .`

## Testing
`poetry run pytest --env-file=./tests/.env.tests`

## Resources
`poetry run task compile_resources`