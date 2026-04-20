## Running

From the project root `/electric-machines`:

```sh
uv run python -m dc_machine.main
uv run python -m dc_machine.examples.01_separately_excited_machine
```

## Testing

From the project root `/electric-machines`:

```sh
uv run python -m pytest dc_machine/tests -v
```

If working from `/electric-machines/dc_machine`, run with the project root explicitly:

```sh
uv run --project .. python -m dc_machine.main
uv run --project .. python -m dc_machine.examples.01_separately_excited_machine
uv run --project .. python -m pytest tests -v
```
