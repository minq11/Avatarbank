# Makefile for Docker commands
#
# 운영 서버에서 가장 자주 쓰는 것:
#   make deploy   — 최신 코드 받아 다시 빌드하고 기동, 상태까지 확인
#   make status   — 컨테이너 상태 + 헬스체크
#   make prod-logs — 로그 따라보기

.PHONY: help build up down restart logs clean migrate deploy status health prod-restart translate-test translate-logs

PROD := docker compose -f docker-compose.prod.yml

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# 로컬 개발 환경
# 주의: 아래 build/up/down/restart/logs/ps 는 기본 docker-compose.yml 을 본다.
# 운영 서버(프로덕션 스택만 떠 있는 곳)에서는 prod-* 나 deploy 를 쓸 것.
build: ## Build Docker images (로컬)
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Show logs
	docker compose logs -f

# 개발 모드
dev-up: ## Start development mode (hot reload)
	docker compose -f docker-compose.dev.yml up -d

dev-down: ## Stop development mode
	docker compose -f docker-compose.dev.yml down

dev-logs: ## Show development logs
	docker compose -f docker-compose.dev.yml logs -f

# 운영 환경
deploy: ## 배포 — git pull → 재빌드 → 기동 → 상태 확인 (운영 서버에서 이것만 치면 된다)
	@echo "▸ 최신 코드 받는 중…"
	@git pull --ff-only
	@echo "▸ 빌드·기동 중… (프론트 빌드에 2~4분)"
	@# --build 는 생략하면 안 된다. 프론트는 Vite 가 빌드 시점에 값을 굽기 때문에
	@# 이미지를 다시 만들지 않으면 git pull 을 해도 화면이 그대로다.
	@$(PROD) up -d --build
	@echo "▸ 기동 대기…"
	@sleep 20
	@$(MAKE) --no-print-directory status

status: ## 컨테이너 상태 + 헬스체크
	@$(PROD) ps
	@echo ""
	@$(MAKE) --no-print-directory health

health: ## nginx / 백엔드 응답 확인
	@printf 'nginx   : '; curl -sf -m 5 http://localhost/healthz || echo '✗ 응답 없음'
	@printf 'backend : '; curl -sfk -m 10 https://localhost/api/health || echo '✗ 응답 없음'
	@echo ""

translate-test: ## 번역 동작 확인 (크레딧 소모 없음). 예: make translate-test P="노을 지는 바닷가"
	@$(PROD) exec -T backend python -m app.translate $(if $(P),"$(P)",)

translate-logs: ## 번역 로그만 추려 보기
	@$(PROD) logs backend --tail 200 | grep -i "번역" || echo "번역 로그가 아직 없습니다 (생성을 한 번 해보세요)"

prod-build: ## Build production images
	$(PROD) build

prod-up: ## Start production services
	$(PROD) up -d

prod-down: ## Stop production services
	$(PROD) down

prod-restart: ## 컨테이너만 재시작 (이미지는 그대로 — 코드를 바꿨다면 deploy 를 쓸 것)
	@# 코드는 Dockerfile 의 COPY 로 이미지에 구워진다. 재시작만으로는 새 코드가
	@# 들어가지 않으니, .env 만 바꿨을 때 쓰는 명령이다.
	$(PROD) restart

prod-logs: ## Show production logs
	$(PROD) logs -f

# 데이터베이스
migrate: ## Run database migrations
	docker compose exec backend python migrations/create_tables.py

migrate-dev: ## Run database migrations (dev mode)
	docker compose -f docker-compose.dev.yml exec backend python migrations/create_tables.py

migrate-prod: ## Run database migrations (production)
	$(PROD) exec backend python migrations/create_tables.py

# 유틸리티
clean: ## Remove all containers, volumes, and images
	docker compose down -v
	docker compose -f docker-compose.dev.yml down -v
	$(PROD) down -v
	docker system prune -f

shell-backend: ## Open shell in backend container
	docker compose exec backend bash

shell-frontend: ## Open shell in frontend container
	docker compose exec frontend sh

ps: ## Show running containers
	docker compose ps
