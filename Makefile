all: lint test
.PHONY: all

lint:
	pipenv run flake8
.PHONY: lint

test:
	pipenv run pytest -v
.PHONY: test

test_cov:
	pipenv run pytest -v --cov . --cov-report term-missing
.PHONY: test

dev_install:
	pipenv install --dev
