# Makefile for Docker commands

.PHONY: help build up down restart logs clean migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# 로컬 개발 환경
build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs
	docker-compose logs -f

# 개발 모드
dev-up: ## Start development mode (hot reload)
	docker-compose -f docker-compose.dev.yml up -d

dev-down: ## Stop development mode
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## Show development logs
	docker-compose -f docker-compose.dev.yml logs -f

# 운영 환경
prod-build: ## Build production images
	docker-compose -f docker-compose.prod.yml build

prod-up: ## Start production services
	docker-compose -f docker-compose.prod.yml up -d

prod-down: ## Stop production services
	docker-compose -f docker-compose.prod.yml down

prod-logs: ## Show production logs
	docker-compose -f docker-compose.prod.yml logs -f

# 데이터베이스
migrate: ## Run database migrations
	docker-compose exec backend python migrations/create_tables.py

migrate-dev: ## Run database migrations (dev mode)
	docker-compose -f docker-compose.dev.yml exec backend python migrations/create_tables.py

migrate-prod: ## Run database migrations (production)
	docker-compose -f docker-compose.prod.yml exec backend python migrations/create_tables.py

# 유틸리티
clean: ## Remove all containers, volumes, and images
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.prod.yml down -v
	docker system prune -f

shell-backend: ## Open shell in backend container
	docker-compose exec backend bash

shell-frontend: ## Open shell in frontend container
	docker-compose exec frontend sh

ps: ## Show running containers
	docker-compose ps
