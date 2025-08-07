install:
	pip install .

test:
	pytest

build:
	poetry build

unit-tests:
	poetry run python -m pytest -v

publish:
	poetry publish --build

clean:
	rm -rf dist build *.egg-info

lint:
	poetry run black .
	poetry run ruff check --fix .

dev: lint
	poetry run pyright .

lint-check:
	poetry run black --check .
	poetry run ruff check .
	poetry run pyright .

# coverage:
# 	poetry run coverage run --branch --source=platzky_hotjar -m pytest -m "not skip_coverage"
# 	poetry run coverage lcov

# html-cov: coverage
# 	poetry run coverage html