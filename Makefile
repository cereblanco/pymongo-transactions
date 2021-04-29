.PHONY: rebuild build up_database up down sample_transaction test

build:
	docker-compose build

rebuild:
	docker-compose build --no-cache

up_database:
	docker-compose up -d mongodb

up: up_database
	@sleep 3
	docker-compose run -e MONGODB_URL=mongodb://mongodb:27017/dev pymongo-app  bash

down:
	docker-compose down

sample_transaction: up_database
	@sleep 3
	docker-compose run -T  -e MONGODB_URL=mongodb://mongodb:27017/dev --rm pymongo-app  poetry run sample_transaction
	
test: up_database
	@sleep 3
	docker-compose run -T  -e MONGODB_URL=mongodb://mongodb:27017/test --rm pymongo-app  poetry run pytest tests/
