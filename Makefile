build: backend frontend
	docker build -t set .
.PHONY: build

frontend:
	$(MAKE) -C frontend
.PHONY: frontend

backend:
	git archive --format=tar.gz --prefix=set/ -o backend.tar.gz HEAD backend
.PHONY: backend
