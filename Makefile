.PHONY: setup lint test

setup:
	uv sync
	@if [ -f .hooks/commit-msg ]; then install -m 755 .hooks/commit-msg .git/hooks/commit-msg; fi
	mkdir -p data artifacts build

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest || [ $$? -eq 5 ]
