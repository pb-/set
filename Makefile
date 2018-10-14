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
	docker run -i --rm \
		smithmicro/uglifyjs --compress 'pure_funcs="F2,F3,F4,F5,F6,F7,F8,F9,A2,A3,A4,A5,A6,A7,A8,A9",pure_getters,keep_fargs=false,unsafe_comps,unsafe' < frontend/public/app.js | \
		docker run -i --rm \
			-u $(shell id -u):$(shell id -g) \
			smithmicro/uglifyjs --mangle > frontend/public/app.min.js
	mv frontend/public/app.min.js frontend/public/app.js
.PHONY: frontend

backend:
	git archive --format=tar.gz --prefix=set/ -o backend.tar.gz HEAD backend
.PHONY: backend

publish:
	docker tag set pbgh/set
	docker push pbgh/set
.PHONY: publish
