## 📋 목차

- [주요 기능](#-주요-기능)
- [빠른 시작](#-빠른-시작)
- [개발 명령어](#-개발-명령어)
- [API 문서](#-api-문서)
- [프로젝트 구조](#️-프로젝트-구조)
- [기술 스택](#️-기술-스택)
- [개발 환경 설정](#-개발-환경-설정)

## ✨ 주요 기능

- 🔐 **JWT 기반 인증시스템**: 안전한 사용자 인증 및 권한 관리
- 📋 **게시판 관리**: 공개/비공개 게시판 생성 및 관리  
- 📝 **게시글 CRUD**: 게시글 생성, 조회, 수정, 삭제

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/LimJiAn/fastapi-example
cd fastapi-example
```

### 2. 환경 변수 설정
```bash
cp .env.example .env
```

### 3. 서버 시작
```bash
# Docker 컨테이너 빌드 및 시작
make build
make up

# 데이터베이스 마이그레이션
make migrate

# 더미 데이터 생성 (선택사항)
make seed
```

### 4. 서버 접속
- **API 문서**: http://localhost:8000/docs

## 🛠 개발 명령어

### Docker 관리
```bash
make build      # Docker 이미지 빌드
make up         # 컨테이너 시작
make down       # 컨테이너 중지
make restart    # 컨테이너 재시작
make logs       # 로그 확인
```

### 데이터베이스 관리
```bash
make migrate    # 마이그레이션 실행
make seed       # 더미 데이터 생성 (10명, 20개 게시판, 100개 게시글)
```

### 테스트 실행
```bash
make test       # 전체 테스트 실행
```

### 모든 명령어 보기
```bash
make help       # 사용 가능한 모든 명령어 확인
```

## 📚 API 문서

서버 실행 후 브라우저에서 접속하여 대화형 API 문서를 확인할 수 있습니다.

- **Swagger UI**: http://localhost:8000/docs - 테스트 가능한 대화형 문서
- **ReDoc**: http://localhost:8000/redoc - 깔끔한 문서 형태

## 🏗️ 프로젝트 구조

```
fastapi-example/
├── app/                        # 메인 애플리케이션
│   ├── api/v1/                 # API v1 라우터
│   │   ├── endpoints/          # API 엔드포인트
│   │   │   ├── auth.py         # 인증 관련 API
│   │   │   ├── board.py        # 게시판 API
│   │   │   └── post.py         # 게시글 API
│   │   └── deps.py             # 의존성 주입
│   ├── core/                   # 핵심 설정
│   │   ├── config.py           # 환경 설정
│   │   ├── security.py         # 보안 (JWT, 암호화)
│   │   └── exceptions.py       # 커스텀 예외 처리
│   │   └── session.py          # client session 관리
│   ├── crud/                   # 데이터 접근 계층 (CRUD)
│   │   ├── base.py             # 기본 CRUD 클래스 (Generic)
│   │   ├── user.py             # 사용자 CRUD 연산
│   │   ├── board.py            # 게시판 CRUD 연산
│   │   └── post.py             # 게시글 CRUD 연산
│   ├── db/                     # 데이터베이스
│   │   └── base_class.py       # SQLAlchemy DeclarativeBase 정의
│   │   └── base.py             # 모든 모델 import 및 Base 노출
│   │   ├── session.py          # DB 세션 관리
│   ├── models/                 # SQLAlchemy 모델
│   │   ├── user.py             # 사용자 모델
│   │   ├── board.py            # 게시판 모델
│   │   └── post.py             # 게시글 모델
│   ├── redis/                  # Redis
│   │   ├── session.py          # Redis 세션 관리
│   ├── schemas/                # Pydantic 스키마
│   ├── services/               # 비즈니스 로직 계층
│   │   ├── auth.py             # 인증 서비스 (JWT, 로그인)
│   │   ├── board.py            # 게시판 서비스 로직
│   │   └── post.py             # 게시글 서비스 로직
│   └── main.py                 # FastAPI 앱 진입점
├── scripts/                    # 유틸리티 스크립트
│   ├── create_dummy_data.py    # 더미 데이터 생성
│   └── create_dummy_data.sh    # Docker용 래퍼 스크립트
├── tests/                      # 테스트 코드
├── migrations/                 # Alembic 마이그레이션
├── Makefile                    # 개발 명령어 모음
├── docker-compose.yml          # Docker Compose 설정
├── Dockerfile                  # Docker 이미지 빌드 설정
└── requirements.txt            # Python 패키지 의존성
```

## 📈 확장 가능한 아키텍처

### 계층별 분리
- **API Layer**: 라우팅과 요청/응답 처리
- **Service Layer**: 비즈니스 로직과 트랜잭션 관리
- **CRUD Layer**: 데이터 접근과 쿼리 최적화
- **Model Layer**: 데이터베이스 스키마 정의

## 🛠️ 기술 스택

### Backend Framework
- **FastAPI** 0.116.1: 고성능 비동기 웹 프레임워크
- **Python** 3.13: 최신 Python 버전

### Database & ORM
- **PostgreSQL** 13: 관계형 데이터베이스
- **SQLAlchemy** 2.0: 현대적인 ORM
- **Alembic**: 데이터베이스 마이그레이션

### Authentication & Security
- **JWT**: JSON Web Token 인증
- **Passlib**: 비밀번호 해싱 (bcrypt)
- **Python-JOSE**: JWT 처리

### Development & Infrastructure
- **Docker & Docker Compose**: 컨테이너화
- **Redis**: 세션 스토리지
- **Uvicorn**: ASGI 서버
- **Pydantic** v2: 데이터 검증

## 🧪 테스트

### 테스트 실행
```bash
# 전체 테스트 실행
make test
```

## 👽 더미 데이터

### 자동 생성
```bash
make seed       # 기본: 10명, 100개 게시판, 1000개 게시글
```

### 수동 생성
```bash
# 사용자 수, 게시판 수, 게시글 수 지정
bash scripts/create_dummy_data.sh 50 100 1000
```

## 🗃️ 데이터베이스 설계

### ERD (Entity Relationship Diagram)
```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    users    │         │   boards    │         │    posts    │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ id (PK)     │────┐    │ id (PK)     │─────────│ id (PK)     │────┐
│ fullname    │    │    │ name        │         │ title       │    │
│ email       │    │    │ public      │         │ content     │    │
│ password    │    │    │ owner_id(FK)│         │ board_id(FK)│◄───┘
│ created_at  │    │    │ posts_count │         │ owner_id(FK)│◄───┐
│ updated_at  │    │    │ created_at  │         │ created_at  │    │
└─────────────┘    │    │ updated_at  │         │ updated_at  │    │
                   │    └─────────────┘         └─────────────┘    │
                   └───────────────────────────────────────────────┘
```

### 주요 제약 조건
- `users.email`: UNIQUE 제약
- `boards.name`: UNIQUE 제약  
- `posts.board_id`: CASCADE DELETE
- `posts.owner_id`: CASCADE DELETE

## 🔧 개발 환경 설정

### Docker 사용
```bash
# 전체 환경 한 번에 시작
make build && make up
```

### 로컬 개발 (Poetry 사용)
```bash
# 1. Poetry 설치 (처음 한 번만)
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/Users/$USER/.local/bin:$PATH"

# 2. 의존성 설치
poetry install

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 4. 데이터베이스만 시작
docker-compose up -d postgres redis

# 5. 마이그레이션 실행
poetry run alembic upgrade head

# 6. 개발 서버 실행
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
