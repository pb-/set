# set

Implements a fun game.

## Deployment

### Build and run a Docker image

```
make
docker run -p 8000:8000 set
```

## Development

### Backend

The backend lives in `backend/`. One-time environment setup (`pipenv` is required):

```
make dev_install
```

Start the sever.

```
make develop
```

### Frontend

The frontend lives in `frontend/` and is written in Elm 0.18 (required on your system). To build:

```
make
```

Build artifacts are in `fontend/public/`.
