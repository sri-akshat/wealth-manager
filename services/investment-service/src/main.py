from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from .core.database import get_db, engine
from .models.investment import Base, MutualFund, Investment, InvestmentStatus, FundCategory
from .schemas.investment import (
    MutualFundCreate,
    MutualFundResponse,
    InvestmentCreate,
    InvestmentResponse,
    PortfolioSummary
)
import jwt
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Investment Service")

# Add sample data function
def add_sample_funds(db: Session):
    # Check if we already have funds
    if db.query(MutualFund).first():
        return

    sample_funds = [
        {
            "scheme_code": "HDFC001",
            "scheme_name": "HDFC Top 100 Fund",
            "category": FundCategory.EQUITY,
            "nav": 100.50,
            "aum": 1000000000,
            "risk_level": "HIGH",
            "expense_ratio": 1.5
        },
        {
            "scheme_code": "ICICI001",
            "scheme_name": "ICICI Prudential Bluechip Fund",
            "category": FundCategory.EQUITY,
            "nav": 75.25,
            "aum": 800000000,
            "risk_level": "HIGH",
            "expense_ratio": 1.2
        },
        {
            "scheme_code": "SBI001",
            "scheme_name": "SBI Debt Fund",
            "category": FundCategory.DEBT,
            "nav": 25.75,
            "aum": 500000000,
            "risk_level": "LOW",
            "expense_ratio": 0.8
        }
    ]

    for fund_data in sample_funds:
        fund = MutualFund(**fund_data)
        db.add(fund)

    db.commit()

# Add endpoint to initialize sample data
@app.post("/initialize-sample-data")
async def initialize_data(db: Session = Depends(get_db)):
    add_sample_funds(db)
    return {"message": "Sample data initialized"}

async def get_current_user_id(authorization: str = Header(...)) -> str:
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, "your-secret-key-here", algorithms=["HS256"])
        return payload.get("sub")  # This will return the email
    except:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

# ... (rest of the endpoints remain the same)

@app.post("/investments", response_model=InvestmentResponse)
async def create_investment(
        investment: InvestmentCreate,
        db: Session = Depends(get_db),
        user_email: str = Depends(get_current_user_id)
):
    fund = db.query(MutualFund).filter(MutualFund.id == investment.fund_id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    units = investment.purchase_amount / fund.nav
    db_investment = Investment(
        user_id=hash(user_email),  # Using hash of email as user_id
        fund_id=investment.fund_id,
        units=units,
        purchase_nav=fund.nav,
        current_nav=fund.nav,
        purchase_amount=investment.purchase_amount,
        current_value=investment.purchase_amount,
        status=InvestmentStatus.COMPLETED
    )

    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    return db_investment
