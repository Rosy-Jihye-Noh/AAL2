"""
FastAPI Backend - Quote Request System
Main Application Entry Point
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import random
import string

from database import get_db, engine
from models import Base, Port, ContainerType, TruckType, Incoterm, Customer, QuoteRequest, CargoDetail
from schemas import (
    PortResponse, ContainerTypeResponse, TruckTypeResponse, IncotermResponse,
    QuoteRequestCreate, QuoteRequestResponse, QuoteSubmitResponse, APIResponse
)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Quote Request API",
    description="API for handling international shipping quote requests",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def generate_request_number() -> str:
    """Generate unique request number: QR-YYYYMMDD-XXX"""
    date_str = datetime.now().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.digits, k=3))
    return f"QR-{date_str}-{random_str}"


def parse_datetime(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    if not date_str:
        return None
    
    # Try different formats
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Invalid date format: {date_str}")


# ==========================================
# ROOT ENDPOINT
# ==========================================

@app.get("/")
def root():
    return {
        "message": "Quote Request API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


# ==========================================
# REFERENCE DATA ENDPOINTS
# ==========================================

@app.get("/api/ports", response_model=List[PortResponse], tags=["Reference Data"])
def get_ports(
    port_type: Optional[str] = None,
    country_code: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get list of ports/airports for POL/POD autocomplete
    
    - port_type: filter by 'ocean', 'air', or 'both'
    - country_code: filter by country (e.g., 'KR', 'CN', 'US')
    - search: search by name or code
    - limit: max number of results (default 50, max 200)
    """
    query = db.query(Port).filter(Port.is_active == True)
    
    if port_type:
        if port_type == "both":
            query = query.filter(Port.port_type.in_(["ocean", "air", "both"]))
        else:
            query = query.filter(Port.port_type.in_([port_type, "both"]))
    
    if country_code:
        query = query.filter(Port.country_code == country_code.upper())
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Port.name.ilike(search_term)) |
            (Port.name_ko.ilike(search_term)) |
            (Port.code.ilike(search_term))
        )
    
    # Apply limit (max 200)
    limit = min(limit, 200)
    return query.order_by(Port.country_code, Port.name).limit(limit).all()


@app.get("/api/container-types", response_model=List[ContainerTypeResponse], tags=["Reference Data"])
def get_container_types(db: Session = Depends(get_db)):
    """Get list of container types for FCL shipments"""
    return db.query(ContainerType).filter(
        ContainerType.is_active == True
    ).order_by(ContainerType.sort_order).all()


@app.get("/api/truck-types", response_model=List[TruckTypeResponse], tags=["Reference Data"])
def get_truck_types(db: Session = Depends(get_db)):
    """Get list of truck types for FTL shipments"""
    return db.query(TruckType).filter(
        TruckType.is_active == True
    ).order_by(TruckType.sort_order).all()


@app.get("/api/incoterms", response_model=List[IncotermResponse], tags=["Reference Data"])
def get_incoterms(db: Session = Depends(get_db)):
    """Get list of Incoterms"""
    return db.query(Incoterm).filter(
        Incoterm.is_active == True
    ).order_by(Incoterm.sort_order).all()


# ==========================================
# QUOTE REQUEST ENDPOINTS
# ==========================================

@app.post("/api/quote/request", response_model=QuoteSubmitResponse, tags=["Quote"])
def submit_quote_request(
    request_data: QuoteRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a new quote request
    
    This endpoint receives the complete quote request form data and stores it in the database.
    """
    try:
        # Check if customer exists by email
        customer = db.query(Customer).filter(
            Customer.email == request_data.customer.email
        ).first()
        
        if not customer:
            # Create new customer
            customer = Customer(
                company=request_data.customer.company,
                job_title=request_data.customer.job_title,
                name=request_data.customer.name,
                email=request_data.customer.email,
                phone=request_data.customer.phone
            )
            db.add(customer)
            db.flush()  # Get customer ID
        else:
            # Update existing customer info
            customer.company = request_data.customer.company
            customer.job_title = request_data.customer.job_title
            customer.name = request_data.customer.name
            customer.phone = request_data.customer.phone
        
        # Generate request number
        request_number = generate_request_number()
        
        # Ensure unique request number
        while db.query(QuoteRequest).filter(QuoteRequest.request_number == request_number).first():
            request_number = generate_request_number()
        
        # Parse dates
        etd = parse_datetime(request_data.etd)
        eta = parse_datetime(request_data.eta) if request_data.eta else None
        
        # Create quote request
        quote_request = QuoteRequest(
            request_number=request_number,
            trade_mode=request_data.trade_mode,
            shipping_type=request_data.shipping_type,
            load_type=request_data.load_type,
            incoterms=request_data.incoterms,
            pol=request_data.pol,
            pod=request_data.pod,
            etd=etd,
            eta=eta,
            is_dg=request_data.is_dg,
            dg_class=request_data.dg_class,
            dg_un=request_data.dg_un,
            export_cc=request_data.export_cc,
            import_cc=request_data.import_cc,
            shipping_insurance=request_data.shipping_insurance,
            pickup_required=request_data.pickup_required,
            pickup_address=request_data.pickup_address,
            delivery_required=request_data.delivery_required,
            delivery_address=request_data.delivery_address,
            invoice_value=request_data.invoice_value,
            remark=request_data.remark,
            status="pending",
            customer_id=customer.id
        )
        db.add(quote_request)
        db.flush()  # Get quote_request ID
        
        # Create cargo details
        for idx, cargo_data in enumerate(request_data.cargo):
            cargo = CargoDetail(
                quote_request_id=quote_request.id,
                row_index=idx,
                container_type=cargo_data.container_type,
                truck_type=cargo_data.truck_type,
                length=cargo_data.length,
                width=cargo_data.width,
                height=cargo_data.height,
                qty=cargo_data.qty,
                gross_weight=cargo_data.gross_weight,
                cbm=cargo_data.cbm,
                volume_weight=cargo_data.volume_weight,
                chargeable_weight=cargo_data.chargeable_weight
            )
            db.add(cargo)
        
        db.commit()
        
        return QuoteSubmitResponse(
            success=True,
            message="Quote request submitted successfully",
            request_number=request_number,
            quote_request_id=quote_request.id
        )
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/quote/requests", tags=["Quote"])
def get_quote_requests(
    status: Optional[str] = None,
    trade_mode: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get list of quote requests with filters
    """
    query = db.query(QuoteRequest).join(Customer)
    
    if status:
        query = query.filter(QuoteRequest.status == status)
    
    if trade_mode:
        query = query.filter(QuoteRequest.trade_mode == trade_mode)
    
    total = query.count()
    requests = query.order_by(QuoteRequest.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": r.id,
                "request_number": r.request_number,
                "trade_mode": r.trade_mode,
                "shipping_type": r.shipping_type,
                "load_type": r.load_type,
                "pol": r.pol,
                "pod": r.pod,
                "etd": r.etd.isoformat() if r.etd else None,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "customer_company": r.customer.company,
                "customer_name": r.customer.name
            }
            for r in requests
        ]
    }


@app.get("/api/quote/request/{request_id}", response_model=QuoteRequestResponse, tags=["Quote"])
def get_quote_request(request_id: int, db: Session = Depends(get_db)):
    """
    Get detailed quote request by ID
    """
    quote_request = db.query(QuoteRequest).filter(QuoteRequest.id == request_id).first()
    
    if not quote_request:
        raise HTTPException(status_code=404, detail="Quote request not found")
    
    return quote_request


@app.patch("/api/quote/request/{request_id}/status", tags=["Quote"])
def update_quote_status(
    request_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Update quote request status
    
    Valid statuses: pending, processing, quoted, accepted, rejected, cancelled
    """
    valid_statuses = ["pending", "processing", "quoted", "accepted", "rejected", "cancelled"]
    
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    quote_request = db.query(QuoteRequest).filter(QuoteRequest.id == request_id).first()
    
    if not quote_request:
        raise HTTPException(status_code=404, detail="Quote request not found")
    
    quote_request.status = status
    db.commit()
    
    return APIResponse(
        success=True,
        message=f"Status updated to '{status}'",
        data={"request_id": request_id, "new_status": status}
    )


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

