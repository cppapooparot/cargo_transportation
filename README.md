# cargo_transportation

## Run
```sh
cp .env.example .env
docker compose up --build
```

## Migrations
```sh
docker exec -it cargo_api alembic revision --autogenerate -m "init"
docker exec -it cargo_api alembic upgrade head
```

## Health
http://localhost:8000/health