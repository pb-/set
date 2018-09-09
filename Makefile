all: lint test
.PHONY: all

lint:
	pipenv run flake8
.PHONY: lint

test:
	pipenv run pytest -v
.PHONY: test

dev_install:
	pipenv install --dev
