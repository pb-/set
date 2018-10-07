FROM python:3.6-alpine

ADD backend.tar.gz /tmp
RUN pip install /tmp/set/backend

COPY frontend/public /app

CMD ["setd", "--root", "/app", "--port", "8000"]
