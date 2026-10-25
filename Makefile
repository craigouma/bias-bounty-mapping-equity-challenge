.PHONY: setup lint test validate sub-ready kaggle-code

setup:
	uv sync
	@if [ -f .hooks/commit-msg ]; then install -m 755 .hooks/commit-msg .git/hooks/commit-msg; fi
	mkdir -p data artifacts build

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest || [ $$? -eq 5 ]

validate:
	uv run python scripts/validate_submission.py $(SUB)

sub-ready:
	uv run python scripts/log_submission.py register --sub $(SUB) --id $(ID) \
		--hypothesis "$(HYP)" --change "$(CHANGE)" --expect "$(EXPECT)" --informs "$(INFORMS)" \
		$(if $(RUN),--run-id $(RUN))

kaggle-code:
	uv run python scripts/kaggle_code_push.py
