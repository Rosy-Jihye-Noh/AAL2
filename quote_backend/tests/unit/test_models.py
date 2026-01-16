"""
Unit Tests for Quote Backend Database Models
Tests for SQLAlchemy models and enums
"""
import pytest
import sys
from pathlib import Path

# Add quote_backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models import (
    TradeModeEnum, ShippingTypeEnum, QuoteStatusEnum,
    BiddingStatusEnum, BidStatusEnum,
    Port, ContainerType, TruckType, Incoterm
)


class TestEnums:
    """Tests for model enums"""
    
    def test_trade_mode_enum_values(self):
        """Test TradeModeEnum has expected values"""
        assert TradeModeEnum.export.value == "export"
        assert TradeModeEnum.import_.value == "import"
        assert TradeModeEnum.domestic.value == "domestic"
    
    def test_shipping_type_enum_values(self):
        """Test ShippingTypeEnum has expected values"""
        assert ShippingTypeEnum.ocean.value == "ocean"
        assert ShippingTypeEnum.air.value == "air"
        assert ShippingTypeEnum.truck.value == "truck"
        assert ShippingTypeEnum.all.value == "all"
    
    def test_quote_status_enum_values(self):
        """Test QuoteStatusEnum has expected values"""
        assert QuoteStatusEnum.pending.value == "pending"
        assert QuoteStatusEnum.processing.value == "processing"
        assert QuoteStatusEnum.quoted.value == "quoted"
        assert QuoteStatusEnum.accepted.value == "accepted"
        assert QuoteStatusEnum.rejected.value == "rejected"
        assert QuoteStatusEnum.cancelled.value == "cancelled"
    
    def test_bidding_status_enum_values(self):
        """Test BiddingStatusEnum has expected values"""
        assert BiddingStatusEnum.open.value == "open"
        assert BiddingStatusEnum.closed.value == "closed"
        assert BiddingStatusEnum.awarded.value == "awarded"
        assert BiddingStatusEnum.cancelled.value == "cancelled"
        assert BiddingStatusEnum.expired.value == "expired"
    
    def test_bid_status_enum_values(self):
        """Test BidStatusEnum has expected values"""
        assert BidStatusEnum.draft.value == "draft"
        assert BidStatusEnum.submitted.value == "submitted"
        assert BidStatusEnum.awarded.value == "awarded"
        assert BidStatusEnum.rejected.value == "rejected"
    
    def test_enum_string_representation(self):
        """Test enum string representation"""
        assert str(TradeModeEnum.export) == "TradeModeEnum.export"
        assert TradeModeEnum.export.value == "export"


class TestPortModel:
    """Tests for Port model"""
    
    def test_port_repr(self):
        """Test Port string representation"""
        port = Port(
            code="KRPUS",
            name="Busan Port",
            country="South Korea",
            country_code="KR",
            port_type="ocean"
        )
        
        repr_str = repr(port)
        assert "KRPUS" in repr_str
        assert "Busan" in repr_str
    
    def test_port_default_values(self):
        """Test Port default values"""
        port = Port(
            code="TEST",
            name="Test Port",
            country="Test",
            country_code="TS",
            port_type="ocean"
        )
        
        assert port.is_active is True


class TestContainerTypeModel:
    """Tests for ContainerType model"""
    
    def test_container_type_repr(self):
        """Test ContainerType string representation"""
        container = ContainerType(
            code="40HC",
            name="40 High Cube"
        )
        
        repr_str = repr(container)
        assert "40HC" in repr_str
    
    def test_container_type_default_values(self):
        """Test ContainerType default values"""
        container = ContainerType(
            code="TEST",
            name="Test Container"
        )
        
        assert container.is_active is True
        assert container.sort_order == 0
        assert container.cbm_limit is False


class TestTruckTypeModel:
    """Tests for TruckType model"""
    
    def test_truck_type_repr(self):
        """Test TruckType string representation"""
        truck = TruckType(
            code="5T_WING",
            name="5T Wing Body"
        )
        
        repr_str = repr(truck)
        assert "5T_WING" in repr_str


class TestIncotermModel:
    """Tests for Incoterm model"""
    
    def test_incoterm_repr(self):
        """Test Incoterm string representation"""
        incoterm = Incoterm(
            code="FOB",
            name="Free On Board"
        )
        
        repr_str = repr(incoterm)
        assert "FOB" in repr_str


class TestModelRelationships:
    """Tests for model relationships (require database session)"""
    
    @pytest.fixture
    def db_session(self):
        """Create in-memory database session"""
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database import Base
        
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(bind=engine)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        yield session
        
        session.close()
        Base.metadata.drop_all(bind=engine)
    
    def test_create_port_in_db(self, db_session):
        """Test creating port in database"""
        port = Port(
            code="KRPUS",
            name="Busan Port",
            country="South Korea",
            country_code="KR",
            port_type="ocean"
        )
        
        db_session.add(port)
        db_session.commit()
        
        # Query back
        result = db_session.query(Port).filter(Port.code == "KRPUS").first()
        
        assert result is not None
        assert result.name == "Busan Port"
    
    def test_create_container_type_in_db(self, db_session):
        """Test creating container type in database"""
        container = ContainerType(
            code="40HC",
            name="40 High Cube",
            max_weight_kg=26460,
            max_cbm=76.0
        )
        
        db_session.add(container)
        db_session.commit()
        
        result = db_session.query(ContainerType).filter(ContainerType.code == "40HC").first()
        
        assert result is not None
        assert result.max_cbm == 76.0
    
    def test_unique_port_code_constraint(self, db_session):
        """Test unique constraint on port code"""
        from sqlalchemy.exc import IntegrityError
        
        port1 = Port(
            code="KRPUS",
            name="Busan Port",
            country="South Korea",
            country_code="KR",
            port_type="ocean"
        )
        
        port2 = Port(
            code="KRPUS",  # Duplicate code
            name="Another Port",
            country="South Korea",
            country_code="KR",
            port_type="ocean"
        )
        
        db_session.add(port1)
        db_session.commit()
        
        db_session.add(port2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


# ============================================================
# Run tests
# ============================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
