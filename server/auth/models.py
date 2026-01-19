"""
User Authentication Models
사용자 인증을 위한 데이터베이스 모델 (암호화 저장 지원)
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import enum
import os

# Database Configuration
AUTH_DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')
AUTH_DATABASE_URL = f"sqlite:///{AUTH_DB_PATH}"

engine = create_engine(
    AUTH_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserType(str, enum.Enum):
    """사용자 유형"""
    shipper = "shipper"       # 화주
    forwarder = "forwarder"   # 포워더


class User(Base):
    """
    사용자 정보 테이블
    비밀번호는 bcrypt로 해시화하여 저장
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 사용자 유형
    user_type = Column(String(20), nullable=False)  # shipper, forwarder
    
    # 기본 정보
    company = Column(String(100), nullable=False)           # 회사명
    business_no = Column(String(20), nullable=True)         # 사업자등록번호
    name = Column(String(50), nullable=False)               # 담당자명
    email = Column(String(100), unique=True, nullable=False, index=True)  # 이메일 (고유)
    phone = Column(String(30), nullable=False)              # 연락처
    
    # 인증 정보 (암호화 저장)
    password_hash = Column(String(255), nullable=False)     # bcrypt 해시화된 비밀번호
    
    # 상태
    is_active = Column(Boolean, default=True)               # 활성 상태
    is_verified = Column(Boolean, default=False)            # 이메일 인증 여부
    
    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)         # 마지막 로그인 시간
    
    def __repr__(self):
        return f"<User {self.email} ({self.user_type})>"


class AIConversation(Base):
    """
    AI 대화 이력 테이블
    사용자별 AI Assistant 대화 내용 저장
    """
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 사용자/세션 정보
    user_id = Column(Integer, nullable=True, index=True)    # 로그인 사용자 ID (비로그인 시 NULL)
    session_id = Column(String(100), nullable=False, index=True)  # 세션 ID
    
    # 대화 내용
    role = Column(String(20), nullable=False)               # 'user' | 'assistant'
    content = Column(String(10000), nullable=False)         # 메시지 내용
    
    # 메타데이터
    tool_used = Column(String(500), nullable=True)          # 사용된 Tool 목록 (JSON)
    quote_data = Column(String(5000), nullable=True)        # 견적 데이터 (JSON)
    navigation = Column(String(500), nullable=True)         # 네비게이션 데이터 (JSON)
    
    # 타임스탬프
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<AIConversation {self.session_id} - {self.role}>"
    
    def to_dict(self):
        """딕셔너리 변환"""
        import json
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "tool_used": json.loads(self.tool_used) if self.tool_used else None,
            "quote_data": json.loads(self.quote_data) if self.quote_data else None,
            "navigation": json.loads(self.navigation) if self.navigation else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


def init_db():
    """데이터베이스 초기화 - 테이블 생성"""
    Base.metadata.create_all(bind=engine)
    print(f"[OK] Auth database initialized: {AUTH_DB_PATH}")


def get_session():
    """데이터베이스 세션 반환"""
    return SessionLocal()


if __name__ == "__main__":
    init_db()
