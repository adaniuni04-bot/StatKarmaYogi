.PHONY: help up down build logs seed test clean

help:
	@echo "India Official Statistical System - Skill Intelligence Platform"
	@echo "---------------------------------------------------------------"
	@echo "make build       - Build Docker containers"
	@echo "make up          - Start all containers in background"
	@echo "make down        - Stop all containers"
	@echo "make logs        - Tail container logs"
	@echo "make seed        - Run database seed script"
	@echo "make test        - Run backend test suite"
	@echo "make clean       - Remove containers and temporary files"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

seed:
	docker compose exec backend python -m app.db.seed.seed_data

test:
	docker compose exec backend pytest -v tests/

clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/app/__pycache__
