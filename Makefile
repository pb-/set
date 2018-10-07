build: backend frontend
	docker build -t set .
.PHONY: build

frontend:
	docker run -it --rm \
		-v "$(shell pwd)/frontend:/code" \
		-w /code \
		-e HOME=/tmp \
		-u $(shell id -u):$(shell id -g) \
		codesimple/elm:0.18 \
			make --yes --output public/app.js set.elm
.PHONY: frontend

backend:
	git archive --format=tar.gz --prefix=set/ -o backend.tar.gz HEAD backend
.PHONY: backend
