#!/bin/bash
echo "🧪 테스트 실행"

# API 통합 테스트 실행
echo "🌐 API Integration Tests 실행 중..."
docker-compose exec api python -m pytest tests/api/v1/endpoints/test_auth.py -v
docker-compose exec api python -m pytest tests/api/v1/endpoints/test_board.py -v
docker-compose exec api python -m pytest tests/api/v1/endpoints/test_post.py -v

# 전체 테스트 실행
# echo "🚀 Tests 실행 중..."
# docker-compose exec api python -m pytest tests/ -v --tb=short

echo "✅ 테스트 완료!"