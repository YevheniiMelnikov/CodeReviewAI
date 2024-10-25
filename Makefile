format:
	ruff check . --fix --config=pyproject.toml
	black . --config=pyproject.toml

check:
	mypy . --config=pyproject.toml

tests:
	@pytest tests -v --ff

.PHONY: tests check format