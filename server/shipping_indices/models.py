"""
Database Models for Shipping Indices (SCFI, CCFI, BDI)

These indices track global shipping freight rates and market conditions.
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


class SCFIIndex(Base):
    """
    SCFI (Shanghai Containerized Freight Index) Model
    
    The Shanghai Containerized Freight Index (SCFI) has been published by the 
    Shanghai Shipping Exchange (SSE) since December 7, 2005. It reflects spot 
    freight rates for container shipping from Shanghai to 15 major destinations.
    
    Originally based on time charter rates, since October 16, 2009, it is 
    calculated based on container freight rates in USD per TEU (20-foot 
    equivalent unit). The index covers CY-CY shipping conditions for 
    General Dry Cargo Containers.
    """
    __tablename__ = 'scfi_index'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 기준일
    index_date = Column(Date, nullable=False, unique=True)
    
    # 지수 정보
    index_code = Column(String(20), default='SCFI')
    index_name = Column(String(100), default='Shanghai Containerized Freight Index')
    
    # 지수 값
    current_index = Column(Float, nullable=False)
    previous_index = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    change_rate = Column(Float, nullable=True)  # 변동률 (%)
    
    # 메타데이터
    source = Column(String(200), default='Shanghai Shipping Exchange (SSE)')
    collected_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_scfi_date', 'index_date'),
        Index('idx_scfi_collected', 'collected_at'),
    )
    
    def to_dict(self):
        """API 응답용 딕셔너리 변환"""
        return {
            'id': self.id,
            'index_date': self.index_date.isoformat() if self.index_date else None,
            'index_code': self.index_code,
            'index_name': self.index_name,
            'current_index': self.current_index,
            'previous_index': self.previous_index,
            'change': self.change,
            'change_rate': self.change_rate,
            'source': self.source,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
        }


class CCFIIndex(Base):
    """
    CCFI (China Containerized Freight Index) Model
    
    The China Containerized Freight Index (CCFI) is compiled by the 
    Shanghai Shipping Exchange under the supervision of China's Ministry 
    of Transport. First published on April 13, 1998, it objectively reflects
    global container market conditions and serves as a key indicator of 
    Chinese shipping market trends.
    
    The index uses January 1, 1998 as the base (1000). It covers 11 major 
    routes from Chinese ports, with freight information from 16 shipping 
    companies, published every Friday.
    """
    __tablename__ = 'ccfi_index'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 기준일
    index_date = Column(Date, nullable=False, unique=True)
    
    # 지수 정보
    index_code = Column(String(20), default='CCFI')
    index_name = Column(String(100), default='China Containerized Freight Index')
    
    # 지수 값
    current_index = Column(Float, nullable=False)
    previous_index = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    change_rate = Column(Float, nullable=True)
    
    # 메타데이터
    source = Column(String(200), default='Shanghai Shipping Exchange (SSE)')
    collected_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_ccfi_date', 'index_date'),
        Index('idx_ccfi_collected', 'collected_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'index_date': self.index_date.isoformat() if self.index_date else None,
            'index_code': self.index_code,
            'index_name': self.index_name,
            'current_index': self.current_index,
            'previous_index': self.previous_index,
            'change': self.change,
            'change_rate': self.change_rate,
            'source': self.source,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
        }


class BDIIndex(Base):
    """
    BDI (Baltic Dry Index) Model
    
    The Baltic Dry Index (BDI) has been used by the Baltic Exchange since 
    November 1, 1999, replacing the BFI (Baltic Freight Index) which tracked 
    dry cargo freight rates since 1985.
    
    Using January 4, 1985 as the base (1000), it is a composite index of 
    time charter rates by vessel type: Baltic Capesize Index (BCI), 
    Baltic Panamax Index (BPI), Baltic Supramax Index (BSI), and 
    Baltic Handysize Index (BHSI). The BDI is calculated by averaging 
    these four indices with equal weights and multiplying by the BDI factor.
    """
    __tablename__ = 'bdi_index'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 기준일
    index_date = Column(Date, nullable=False, unique=True)
    
    # 지수 정보
    index_code = Column(String(20), default='BDI')
    index_name = Column(String(100), default='Baltic Dry Index')
    
    # 지수 값
    current_index = Column(Float, nullable=False)
    previous_index = Column(Float, nullable=True)
    change = Column(Float, nullable=True)
    change_rate = Column(Float, nullable=True)
    
    # 메타데이터
    source = Column(String(200), default='Baltic Exchange')
    collected_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_bdi_date', 'index_date'),
        Index('idx_bdi_collected', 'collected_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'index_date': self.index_date.isoformat() if self.index_date else None,
            'index_code': self.index_code,
            'index_name': self.index_name,
            'current_index': self.current_index,
            'previous_index': self.previous_index,
            'change': self.change,
            'change_rate': self.change_rate,
            'source': self.source,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
        }


# 데이터베이스 연결 유틸리티
def get_shipping_indices_database_url():
    """Shipping Indices 데이터베이스 URL 반환"""
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
    return f"sqlite:///{os.path.join(base_dir, 'shipping_indices.db')}"


def init_shipping_indices_database():
    """데이터베이스 초기화 및 테이블 생성"""
    engine = create_engine(get_shipping_indices_database_url(), echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_shipping_indices_session():
    """새 데이터베이스 세션 반환"""
    engine = create_engine(get_shipping_indices_database_url(), echo=False)
    Session = sessionmaker(bind=engine)
    return Session()

