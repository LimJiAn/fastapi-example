#!/bin/bash
# 사용법:
#   bash scripts/create_dummy_data.sh [사용자수] [게시판수] [게시글수]
# 예시:
#   bash scripts/create_dummy_data.sh 10 100 1000

set -e
# 기본값 설정
USER_COUNT=${1:-10}
BOARD_COUNT=${2:-100}
POST_COUNT=${3:-1000}

echo "🐳 Docker 컨테이너에서 더미 데이터 생성"
echo "📋 생성할 데이터: 사용자 ${USER_COUNT}명, 게시판 ${BOARD_COUNT}개, 게시글 ${POST_COUNT}개"
echo ""

# Faker 라이브러리 설치
echo "📦 Faker 라이브러리 설치 중..."
docker-compose exec api pip install faker

echo ""

# 더미 데이터 생성 실행
echo "🚀 더미 데이터 생성 시작..."
docker-compose exec api python scripts/create_dummy_data.py ${USER_COUNT} ${BOARD_COUNT} ${POST_COUNT}

echo ""
echo "✅ 더미 데이터 생성 완료!"
echo ""
echo "💡 생성된 데이터 확인 방법:"
echo "  - API 테스트: http://localhost:8000/docs"
echo "  - 사용자 로그인: POST /api/v1/auth/login"
echo "    (이메일: 생성된 사용자 중 하나, 비밀번호: qwer1234)"
