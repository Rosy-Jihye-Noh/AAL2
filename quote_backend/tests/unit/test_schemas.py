"""
Unit Tests for Quote Backend Pydantic Schemas
Tests for request/response validation
"""
import pytest
from pydantic import ValidationError
import sys
from pathlib import Path

# Add quote_backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from schemas import (
    PortBase, PortResponse,
    ContainerTypeBase, ContainerTypeResponse,
    TruckTypeBase, TruckTypeResponse,
    IncotermBase, IncotermResponse
)


class TestPortSchema:
    """Tests for Port schemas"""
    
    def test_port_base_valid_data(self):
        """Test PortBase with valid data"""
        port = PortBase(
            code="KRPUS",
            name="Busan Port",
            country="South Korea",
            country_code="KR",
            port_type="ocean"
        )
        
        assert port.code == "KRPUS"
        assert port.name == "Busan Port"
        assert port.is_active is True  # Default value
    
    def test_port_base_with_korean_name(self):
        """Test PortBase with Korean name"""
        port = PortBase(
            code="KRPUS",
            name="Busan Port",
            name_ko="부산항",
            country="South Korea",
            country_code="KR",
            port_type="ocean"
        )
        
        assert port.name_ko == "부산항"
    
    def test_port_base_missing_required_field(self):
        """Test PortBase fails with missing required field"""
        with pytest.raises(ValidationError):
            PortBase(
                code="KRPUS",
                name="Busan Port"
                # Missing: country, country_code, port_type
            )
    
    def test_port_response_includes_id(self):
        """Test PortResponse includes id field"""
        port = PortResponse(
            id=1,
            code="KRPUS",
            name="Busan Port",
            country="South Korea",
            country_code="KR",
            port_type="ocean"
        )
        
        assert port.id == 1


class TestContainerTypeSchema:
    """Tests for ContainerType schemas"""
    
    def test_container_type_base_minimal(self):
        """Test ContainerTypeBase with minimal data"""
        container = ContainerTypeBase(
            code="40HC",
            name="40 High Cube"
        )
        
        assert container.code == "40HC"
        assert container.name == "40 High Cube"
        assert container.is_active is True
    
    def test_container_type_base_full_data(self):
        """Test ContainerTypeBase with all fields"""
        container = ContainerTypeBase(
            code="40HC",
            name="40 High Cube Container",
            abbreviation="40'HC",
            description="High cube dry container",
            size="40",
            category="DC",
            size_teu=2.0,
            iso_standard="45G1",
            max_weight_kg=26460,
            length_mm=12032,
            width_mm=2352,
            height_mm=2698,
            max_cbm=76.0
        )
        
        assert container.max_weight_kg == 26460
        assert container.max_cbm == 76.0
        assert container.size_teu == 2.0
    
    def test_container_type_response_from_attributes(self):
        """Test ContainerTypeResponse with id"""
        container = ContainerTypeResponse(
            id=1,
            code="20DC",
            name="20 Dry Container"
        )
        
        assert container.id == 1


class TestTruckTypeSchema:
    """Tests for TruckType schemas"""
    
    def test_truck_type_base_minimal(self):
        """Test TruckTypeBase with minimal data"""
        truck = TruckTypeBase(
            code="5T_WING",
            name="5T Wing Body"
        )
        
        assert truck.code == "5T_WING"
        assert truck.name == "5T Wing Body"
    
    def test_truck_type_base_with_specs(self):
        """Test TruckTypeBase with specifications"""
        truck = TruckTypeBase(
            code="11T_WING",
            name="11T Wing Body",
            abbreviation="11T 윙",
            max_weight_kg=11000,
            max_cbm=45.0,
            sort_order=2
        )
        
        assert truck.max_weight_kg == 11000
        assert truck.max_cbm == 45.0
        assert truck.sort_order == 2


class TestIncotermSchema:
    """Tests for Incoterm schemas"""
    
    def test_incoterm_base_minimal(self):
        """Test IncotermBase with minimal data"""
        incoterm = IncotermBase(
            code="FOB",
            name="Free On Board"
        )
        
        assert incoterm.code == "FOB"
        assert incoterm.name == "Free On Board"
    
    def test_incoterm_base_full_data(self):
        """Test IncotermBase with all fields"""
        incoterm = IncotermBase(
            code="CIF",
            name="Cost, Insurance and Freight",
            description="Seller pays for transportation and insurance",
            description_ko="매도인이 운송비와 보험료 부담",
            seller_responsibility="Loading, freight, insurance",
            buyer_responsibility="Unloading, customs clearance",
            sort_order=5
        )
        
        assert incoterm.description_ko == "매도인이 운송비와 보험료 부담"
        assert incoterm.sort_order == 5


class TestSchemaValidation:
    """Tests for schema validation edge cases"""
    
    def test_port_code_empty_string(self):
        """Test port code can be empty string (validation depends on business rules)"""
        # This test documents current behavior
        try:
            port = PortBase(
                code="",
                name="Test Port",
                country="Test Country",
                country_code="TC",
                port_type="ocean"
            )
            assert port.code == ""
        except ValidationError:
            # If validation is added, this is also acceptable
            pass
    
    def test_container_negative_weight(self):
        """Test container with negative weight"""
        # Pydantic doesn't validate negative by default
        container = ContainerTypeBase(
            code="TEST",
            name="Test Container",
            max_weight_kg=-1000
        )
        # Should probably add validation in the future
        assert container.max_weight_kg == -1000
    
    def test_schema_dict_conversion(self):
        """Test schema can be converted to dict"""
        port = PortBase(
            code="KRPUS",
            name="Busan",
            country="Korea",
            country_code="KR",
            port_type="ocean"
        )
        
        port_dict = port.model_dump()
        
        assert isinstance(port_dict, dict)
        assert port_dict['code'] == "KRPUS"
    
    def test_schema_json_conversion(self):
        """Test schema can be converted to JSON"""
        port = PortBase(
            code="KRPUS",
            name="Busan",
            country="Korea",
            country_code="KR",
            port_type="ocean"
        )
        
        port_json = port.model_dump_json()
        
        assert isinstance(port_json, str)
        assert "KRPUS" in port_json


# ============================================================
# Run tests
# ============================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
