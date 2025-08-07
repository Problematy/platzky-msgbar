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