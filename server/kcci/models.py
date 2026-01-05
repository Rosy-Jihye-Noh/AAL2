"""
Database Models for KCCI (Korea Container Freight Index)

KCCI 종합지수 및 항로별 지수 저장 모델
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, 
    Index, create_engine, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()


class KCCIIndex(Base):
    """
    KCCI 종합지수 모델
    
    매주 발표되는 KCCI 종합지수 데이터 저장
    """
    __tablename__ = 'kcci_index'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 기준 주차 (발표 기준일)
    week_date = Column(Date, nullable=False, unique=True)
    
    # 지수 정보
    index_code = Column(String(20), default='KCCI')
    index_name = Column(String(100), default='Comprehensive Index')
    
    # 지수 값
    current_index = Column(Float, nullable=False)
    previous_index = Column(Float, nullable=True)
    weekly_change = Column(Float, nullable=True)
    weekly_change_rate = Column(Float, nullable=True)  # 변동률 (%)
    
    # 메타데이터
    source_url = Column(String(500), nullable=True)
    collected_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_kcci_week_date', 'week_date'),
        Index('idx_kcci_collected', 'collected_at'),
    )
    
    def to_dict(self):
        """API 응답용 딕셔너리 변환"""
        return {
            'id': self.id,
            'week_date': self.week_date.isoformat() if self.week_date else None,
            'index_code': self.index_code,
            'index_name': self.index_name,
            'current_index': self.current_index,
            'previous_index': self.previous_index,
            'weekly_change': self.weekly_change,
            'weekly_change_rate': self.weekly_change_rate,
            'source_url': self.source_url,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
        }


class KCCIRouteIndex(Base):
    """
    KCCI 항로별 지수 모델
    
    13개 주요 항로별 운임지수 저장
    """
    __tablename__ = 'kcci_route_index'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 기준 주차
    week_date = Column(Date, nullable=False)
    
    # 항로 정보
    route_group = Column(String(50), nullable=True)  # Mainlane / Non-Mainlane / Intra Asia
    route_code = Column(String(20), nullable=False)  # KUWI, KUEI, etc.
    route_name = Column(String(100), nullable=False)  # USWC, Europe, etc.
    
    # 가중치
    weight = Column(Float, nullable=True)  # 항로 가중치 (%)
    
    # 지수 값
    current_index = Column(Float, nullable=False)
    previous_index = Column(Float, nullable=True)
    weekly_change = Column(Float, nullable=True)
    weekly_change_rate = Column(Float, nullable=True)
    
    # 메타데이터
    source_url = Column(String(500), nullable=True)
    collected_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_kcci_route_week', 'week_date'),
        Index('idx_kcci_route_code', 'route_code'),
        Index('idx_kcci_route_week_code', 'week_date', 'route_code'),
    )
    
    def to_dict(self):
        """API 응답용 딕셔너리 변환"""
        return {
            'id': self.id,
            'week_date': self.week_date.isoformat() if self.week_date else None,
            'route_group': self.route_group,
            'route_code': self.route_code,
            'route_name': self.route_name,
            'weight': self.weight,
            'current_index': self.current_index,
            'previous_index': self.previous_index,
            'weekly_change': self.weekly_change,
            'weekly_change_rate': self.weekly_change_rate,
            'source_url': self.source_url,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
        }


class KCCICollectionLog(Base):
    """
    KCCI 수집 작업 로그
    
    수집 실행 이력 추적
    """
    __tablename__ = 'kcci_collection_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 실행 시간
    executed_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # 결과
    week_date = Column(Date, nullable=True)  # 수집된 데이터의 기준일
    comprehensive_index = Column(Float, nullable=True)  # 수집된 종합지수
    route_count = Column(Integer, default=0)  # 수집된 항로 수
    
    # 상태
    is_success = Column(Integer, default=1)  # 1=성공, 0=실패
    error_message = Column(Text, nullable=True)
    
    # 소요 시간
    duration_seconds = Column(Float, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'week_date': self.week_date.isoformat() if self.week_date else None,
            'comprehensive_index': self.comprehensive_index,
            'route_count': self.route_count,
            'is_success': self.is_success,
            'error_message': self.error_message,
            'duration_seconds': self.duration_seconds,
        }


# 데이터베이스 연결 유틸리티
def get_kcci_database_url():
    """KCCI 데이터베이스 URL 반환"""
    # PostgreSQL 우선 시도
    postgres_url = os.getenv('DATABASE_URL')
    if postgres_url and postgres_url.startswith('postgresql'):
        try:
            import psycopg2
            return postgres_url
        except ImportError:
            pass
    
    # SQLite 폴백
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return f"sqlite:///{os.path.join(base_dir, 'kcci.db')}"


def init_kcci_database():
    """데이터베이스 초기화 및 테이블 생성"""
    engine = create_engine(get_kcci_database_url(), echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_kcci_session():
    """새 데이터베이스 세션 반환"""
    engine = create_engine(get_kcci_database_url(), echo=False)
    Session = sessionmaker(bind=engine)
    return Session()

