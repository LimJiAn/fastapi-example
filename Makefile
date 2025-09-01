.PHONY: help build up down restart logs logs-api test migrations migrate seed reset-db

# 기본 타겟 - 도움말 표시
help:
	@echo "Board API 개발 도구"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make build         Docker 이미지 빌드"
	@echo "  make up            컨테이너 시작"
	@echo "  make down          컨테이너 중지"
	@echo "  make restart       컨테이너 재시작"
	@echo "  make logs          로그 확인"
	@echo "  make logs-api      API 컨테이너 로그 확인"
	@echo ""
	@echo "🗄️  데이터베이스:"
	@echo "  make migrate       마이그레이션 실행"
	@echo "  make seed          더미 데이터 생성"
	@echo ""
	@echo "🧪 테스트:"
	@echo "  make test          테스트 실행"

# Docker Compose 명령어들
build:
	@echo "🔨 Docker 이미지 빌드 중..."
	docker-compose build

up:
	@echo "🚀 컨테이너 시작 중..."
	docker-compose up -d
	@echo "✅ 서버가 시작되었습니다: http://localhost:8000"

down:
	@echo "🛑 컨테이너 중지 중..."
	docker-compose down

restart: down build up

logs:
	docker-compose logs -f

logs-api:
	@echo "📜 API 컨테이너 로그 확인 중..."
	docker-compose logs -f api

migrations:
	@echo "📦 마이그레이션 파일 생성 중..."
	@read -p "마이그레이션 메시지를 입력하세요: " msg; \
	docker-compose exec api alembic revision --autogenerate -m "$$msg"

# 데이터베이스 및 더미 데이터
migrate:
	@echo "🗄️  마이그레이션 실행 중..."
	docker-compose exec api alembic upgrade head

seed:
	@echo "🌱 더미 데이터 생성 중..."
	bash scripts/create_dummy_data.sh 10 100 1000

# 테스트
test:
	@echo "🧪 테스트 실행 중..."
# 	docker-compose exec api python -m pytest tests/api/v1/endpoints/test_auth.py -v
# 	docker-compose exec api python -m pytest tests/api/v1/endpoints/test_board.py -v
# 	docker-compose exec api python -m pytest tests/api/v1/endpoints/test_post.py -v
	docker-compose exec api python -m pytest tests/ -v --tb=short

reset-db:
	@echo "🗑️ 데이터베이스 초기화 중..."
	docker-compose exec api alembic downgrade base
	docker-compose exec api alembic upgrade head
	@echo "✅ 데이터베이스가 초기화되었습니다."