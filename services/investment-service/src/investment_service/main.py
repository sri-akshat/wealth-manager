# src/main.py
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from .core.database import get_db, Base, engine
from .core.auth import get_current_user_id
from .core.config import settings
from .models.investment import MutualFund, Investment, InvestmentStatus, FundCategory
from .schemas.investment import (
    InvestmentCreate,
    InvestmentResponse,
    PortfolioSummary,
    PortfolioInvestment,
    PortfolioAnalytics,
    PortfolioInvestmentList
)
from datetime import datetime

# Create tables if not in test mode
if not settings.TEST_MODE:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Investment service API for wealth manager platform. Manages mutual fund investments and portfolio analytics.",
    version=settings.VERSION,
    contact={
        "name": "Wealth Manager Team",
        "url": "https://github.com/sri-akshat/wealth-manager",
    },
    license_info={
        "name": "Private",
    },
    openapi_tags=[
        {
            "name": "portfolio",
            "description": "Operations related to investment portfolios",
        },
        {
            "name": "investments",
            "description": "Operations for managing individual investments",
        },
        {
            "name": "system",
            "description": "System maintenance operations",
        },
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["system"])
async def root():
    """
    Root endpoint that provides basic service information.
    
    Returns service name, version, and status.
    """
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy"
    }

@app.get("/portfolio/summary", response_model=PortfolioSummary, tags=["portfolio"])
async def get_portfolio_summary(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get summary of user's investment portfolio.
    
    Returns total investment, current value, returns, and asset allocation.
    """
    try:
        investments = Investment.get_user_portfolio(db, user_id)
        if not investments:
            return PortfolioSummary(
                total_investment=0,
                current_value=0,
                total_returns=0,
                returns_percentage=0,
                number_of_investments=0,
                asset_allocation={}
            )

        total_investment = sum(inv.purchase_amount for inv in investments)
        current_value = sum(inv.current_value for inv in investments)
        total_returns = current_value - total_investment
        returns_percentage = (total_returns / total_investment * 100) if total_investment > 0 else 0

        # Calculate asset allocation
        allocation = {}
        for inv in investments:
            category = inv.fund.category.value.lower()  # Convert to lowercase
            allocation[category] = allocation.get(category, 0) + inv.current_value

        total_value = sum(allocation.values())
        asset_allocation = {
            category: (value / total_value * 100)
            for category, value in allocation.items()
        }

        return PortfolioSummary(
            total_investment=total_investment,
            current_value=current_value,
            total_returns=total_returns,
            returns_percentage=returns_percentage,
            number_of_investments=len(investments),
            asset_allocation=asset_allocation
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while fetching portfolio summary"
        )

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
@app.post("/initialize-sample-data", tags=["system"])
async def initialize_data(db: Session = Depends(get_db)):
    """
    Initialize sample mutual fund data for testing.
    
    This endpoint adds a set of predefined mutual funds to the database
    if they don't already exist.
    """
    add_sample_funds(db)
    return {"message": "Sample data initialized"}

@app.post("/investments/", response_model=InvestmentResponse, tags=["investments"])
async def create_investment(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new investment for the user.
    
    Takes investment details and creates a new investment record.
    """
    fund = db.query(MutualFund).filter(MutualFund.id == investment.fund_id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    units = investment.purchase_amount / fund.nav
    db_investment = Investment(
        user_id=user_id,  # Use the user_id from the token
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

@app.get("/portfolio/investments", response_model=PortfolioInvestmentList, tags=["portfolio"])
async def get_portfolio_investments(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get detailed list of user's investments.
    
    Returns a list of all investments in the user's portfolio with calculated
    returns and current values.
    """
    investments = Investment.get_user_portfolio(db, user_id)

    result = []
    for inv in investments:
        returns, returns_percentage = inv.calculate_returns()
        result.append(PortfolioInvestment(
            id=inv.id,
            fund_name=inv.fund.scheme_name,
            category=inv.fund.category,
            units=inv.units,
            purchase_nav=inv.purchase_nav,
            current_nav=inv.current_nav,
            purchase_amount=inv.purchase_amount,
            current_value=inv.current_value,
            returns=returns,
            returns_percentage=returns_percentage,
            purchase_date=inv.purchase_date
        ))

    return PortfolioInvestmentList(investments=result)

@app.get("/portfolio/analytics", response_model=PortfolioAnalytics, tags=["portfolio"])
async def get_portfolio_analytics(
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    """
    Get comprehensive portfolio analytics including summary and investments.
    
    This endpoint combines portfolio summary and detailed investment information
    in a single response for a complete portfolio overview.
    """
    summary = await get_portfolio_summary(db, user_id)
    investments_list = await get_portfolio_investments(db, user_id)

    return PortfolioAnalytics(
        summary=summary,
        investments=investments_list.investments  # Access the investments field
    )

@app.post("/investments/update-navs", tags=["investments"])
async def update_investment_navs(
        db: Session = Depends(get_db),
        user_id: str = Depends(get_current_user_id)
):
    """
    Update current NAVs and values for all investments.
    
    This endpoint recalculates the current value of all investments
    based on the latest NAV data. In a production environment,
    this would fetch real-time NAV data from an external API.
    """
    investments = Investment.get_user_portfolio(db, user_id)

    for investment in investments:
        # In a real implementation, you'd fetch the latest NAV from an external API
        investment.update_current_value()

    db.commit()
    return {"message": "Investment values updated successfully"}

# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    """
    Check if the service is healthy.
    
    Returns a simple status message indicating the service is operational.
    """
    return {"status": "healthy", "service": "investment-service"}
