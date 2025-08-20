"""
더미 데이터 생성 스크립트
"""
import asyncio
import random
import sys
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session
from faker import Faker

from app.db.session import SessionLocal
from app.core.security import get_password_hash
from app.models import User, Board, Post


# 한국어 locale 사용
fake = Faker('ko_KR')


class DummyDataGenerator:
    """더미 데이터 생성기"""
    
    def __init__(self, db: Session):
        self.db = db
        self.users = []
        self.boards = []
        self.posts = []
    
    def create_users(self, count: int = 10) -> list[User]:
        """사용자 더미 데이터 생성"""
        print(f"📝 {count}명의 사용자 생성 중...")
        users = []
        base_domains = ['gmail.com', 'naver.com', 'kakao.com']
        for i in range(count):
            fullname = fake.name()
            # 이메일 중복 방지
            username = fake.user_name().lower()
            domain = random.choice(base_domains)
            email = f"{username}_{i}@{domain}"

            user = User(
                fullname=fullname,
                email=email,
                password=get_password_hash("qwer1234")
            )
            # 생성일을 다양하게 설정 (최근 6개월 내)
            if i > 0:  # 첫 번째 사용자는 현재 시간
                created_days_ago = random.randint(1, 180)
                past_time = datetime.now() - timedelta(days=created_days_ago)
                if hasattr(user.created_at, 'tzinfo') and user.created_at.tzinfo:
                    user.created_at = past_time.replace(tzinfo=user.created_at.tzinfo)
                else:
                    user.created_at = past_time
                user.updated_at = user.created_at
            
            users.append(user)
            
        self.db.add_all(users)
        self.db.commit()

        for user in users:
            self.db.refresh(user)

        self.users = users
        print(f"✅ {len(users)}명의 사용자 생성 완료")
        return users
    
    def create_boards(self, count: int = 200) -> list[Board]:
        """게시판 더미 데이터 생성 (데이터베이스 중복 방지)"""
        print(f"📋 {count}개의 게시판 생성 중...")

        if not self.users:
            raise ValueError("먼저 사용자를 생성해야 합니다.")

        boards = []
        # 데이터베이스에서 기존 게시판 이름 조회
        existing_names = {name[0] for name in self.db.query(Board.name).all()}
        used_names = set(existing_names)  # 기존 + 신규 이름 모두 관리
        
        # 기본 카테고리 후보
        board_categories = [
            "자유게시판", "질문답변", "공지사항", "개발이야기",
            "취업정보", "스터디모집", "프로젝트 공유", "기술토론",
            "일상잡담", "맛집추천", "여행후기", "독서모임",
            "운동모임", "게임이야기", "영화리뷰", "음악감상",
            "취미생활", "사진공유", "애완동물", "기타",
            "연애상담", "자유", "질문", "공지", "개발",
            "일상", "맛집", "여행", "독서", "운동", "게임"
        ]
        
        attempts = 0
        max_attempts = count * 10  # 무한루프 방지
        
        while len(boards) < count and attempts < max_attempts:
            attempts += 1
            base_name = random.choice(board_categories)
            
            # 유니크한 이름 생성 (UUID 뒷자리 사용으로 완전 유니크 보장)
            if random.random() < 0.3:  # 30% 확률로 Faker 단어 추가
                candidate = f"{fake.word().capitalize()} {base_name}"
            else:  # 70% 확률로 UUID 일부 추가 (완전 유니크)
                uuid_suffix = str(uuid.uuid4())[:8]
                candidate = f"{base_name}_{uuid_suffix}"
            
            # 중복 체크
            if candidate in used_names:
                continue
                
            used_names.add(candidate)
            owner = random.choice(self.users)
            public = random.random() < 0.8
            
            board = Board(
                name=candidate,
                public=public,
                owner_id=owner.id,
            )
            # created_at ~ updated_at 랜덤 설정
            owner_created = owner.created_at
            now = owner_created.tzinfo and datetime.now(owner_created.tzinfo) or datetime.now()
            days = max((now - owner_created).days, 0)
            if days > 0:
                d = random.randint(0, days)
                board.created_at = owner_created + timedelta(days=d)
                board.updated_at = board.created_at

            boards.append(board)
        
        if len(boards) < count:
            print(f"⚠️  요청된 {count}개 중 {len(boards)}개만 생성됨 (중복 방지로 인해)")

        # 하나씩 insert해서 중복 오류 방지
        for board in boards:
            try:
                self.db.add(board)
                self.db.flush()  # 즉시 DB에 반영해서 중복 체크
                self.db.refresh(board)
            except Exception as e:
                print(f"⚠️  게시판 '{board.name}' 생성 실패: {str(e)}")
                self.db.rollback()
                boards.remove(board)
                continue
        
        self.db.commit()
        self.boards = boards
        print(f"✅ {len(boards)}개의 게시판 생성 완료")
        return boards

    def create_posts(self, count: int = 1000) -> list[Post]:
        """게시글 더미 데이터 생성"""
        print(f"📝 {count}개의 게시글 생성 중...")
        
        if not self.users or not self.boards:
            raise ValueError("먼저 사용자와 게시판을 생성해야 합니다.")
        posts = []
        # 다양한 게시글 제목 템플릿
        title_templates = [
            "{}에 대해 질문이 있습니다.",
            "{} 어떻게 생각하세요?",
            "{} 관련 정보 공유합니다.",
            "{} 후기 공유해요!",
            "{}를 추천합니다.",
            "{} 문제 해결 방법",
            "{} 경험담을 나눕니다.",
            "{}에 대한 의견을 듣고 싶어요.",
            "{} 관련 팁 공유!",
            "{}를 시작하려는데 조언 부탁드려요."
        ]
        # 주제별 키워드
        topics = [
            "Python 프로그래밍", "웹 개발", "데이터베이스 설계", "API 개발",
            "프론트엔드 개발", "백엔드 개발", "클라우드 서비스", "DevOps",
            "머신러닝", "인공지능", "알고리즘", "자료구조",
            "취업 준비", "면접 경험", "포트폴리오 제작", "이력서 작성",
            "독서 경험", "영화 감상", "여행 후기", "맛집 추천",
            "운동 루틴", "다이어트 방법", "건강 관리", "스트레스 해소"
        ]
        for i in range(count):
            # 랜덤한 게시판과 사용자 선택
            board = random.choice(self.boards)
            author = random.choice(self.users)
            # 제목 생성
            topic = random.choice(topics)
            title_template = random.choice(title_templates)
            title = title_template.format(topic)
            # 내용 생성 (1-5 문단)
            paragraph_count = random.randint(1, 5)
            content_paragraphs = []
            for _ in range(paragraph_count):
                content_paragraphs.append(fake.text(max_nb_chars=200))
            content = "\n\n".join(content_paragraphs)
            post = Post(
                title=title,
                content=content,
                board_id=board.id,
                owner_id=author.id
            )
            # 생성일을 게시판 생성일 이후로 설정
            board_created = board.created_at
            # timezone aware datetime 처리
            if hasattr(board_created, 'tzinfo') and board_created.tzinfo:
                now = datetime.now().replace(tzinfo=board_created.tzinfo)
            else:
                now = datetime.now()

            try:
                max_days = (now - board_created).days
                if max_days > 0:
                    created_days_after = random.randint(0, max_days)
                    post.created_at = board_created + timedelta(
                        days=created_days_after,
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    post.updated_at = post.created_at
                    # 10% 확률로 수정됨
                    if random.random() < 0.1:
                        update_hours = random.randint(1, max((now - post.created_at).days * 24, 1))
                        post.updated_at = post.created_at + timedelta(hours=update_hours)
            except TypeError:
                # timezone 문제가 있으면 그냥 현재 시간 사용
                pass
            
            posts.append(post)

        self.db.add_all(posts)
        self.db.commit()

        for post in posts:
            self.db.refresh(post)

        self.posts = posts
        print(f"✅ {len(posts)}개의 게시글 생성 완료")
        return posts

    def update_board_post_counts(self):
        """게시판별 게시글 수 업데이트 (트리거가 있다면 자동으로 되지만 확실히 하기 위해)"""
        print("🔄 게시판별 게시글 수 업데이트 중...")
        for board in self.boards:
            post_count = self.db.query(Post).filter(Post.board_id == board.id).count()
            board.posts_count = post_count
        self.db.commit()
        print("✅ 게시판 게시글 수 업데이트 완료")
    
    def print_summary(self):
        """생성된 데이터 요약 출력"""
        print("\n" + "="*50)
        print("📊 더미 데이터 생성 완료!")
        print("="*50)
        print(f"👤 사용자: {len(self.users)}명")
        print(f"📋 게시판: {len(self.boards)}개")
        print(f"📝 게시글: {len(self.posts)}개")

        # 게시판별 게시글 수 통계
        print("\n📋 게시판별 게시글 수:")
        for board in sorted(self.boards, key=lambda x: x.posts_count, reverse=True)[:10]:
            print(f"  • {board.name}: {board.posts_count}개")

        print("\n🔗 샘플 사용자 정보:")
        for user in self.users[:5]:
            user_boards = [b for b in self.boards if b.owner_id == user.id]
            user_posts = [p for p in self.posts if p.owner_id == user.id]
            print(f"  • {user.fullname} ({user.email})")
            print(f"    - 게시판: {len(user_boards)}개, 게시글: {len(user_posts)}개")
        print("\n" + "="*50)


def main():
    """메인 함수"""
    print("🚀 더미 데이터 생성을 시작합니다...")
    # 명령행 인수로 개수 조정 가능
    user_count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    board_count = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    post_count = int(sys.argv[3]) if len(sys.argv) > 3 else 1000

    print(f"📋 생성할 데이터: 사용자 {user_count}명, 게시판 {board_count}개, 게시글 {post_count}개")
    
    # 데이터베이스 연결
    db = SessionLocal()
    
    try:
        # 더미 데이터 생성기 초기화
        generator = DummyDataGenerator(db)
        
        # 데이터 생성
        generator.create_users(user_count)
        generator.create_boards(board_count)
        generator.create_posts(post_count)
        
        # 게시판 카운트 업데이트
        generator.update_board_post_counts()
        
        # 결과 요약
        generator.print_summary()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
