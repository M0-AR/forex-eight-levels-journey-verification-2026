build:
	docker compose build
run:
	docker compose run --rm research
figures:
	python3 scripts/make_figures.py
test:
	PYTHONPATH=. python -m pytest tests/ -q
fetch:
	python -m src.fetch_data
all: run figures test
