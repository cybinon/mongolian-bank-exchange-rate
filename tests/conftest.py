import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.main import app
from app.db.database import get_db
from app.models.currency import Base


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test function."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    yield db
    db.close()

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with the test database."""
    return TestClient(app)


@pytest.fixture
def sample_rate_data():
    """Sample exchange rate data for testing."""
    return {
        "usd": {"cash": {"buy": 3420.5, "sell": 3450.0}, "noncash": {"buy": 3415.0, "sell": 3455.0}},
        "eur": {"cash": {"buy": 3720.0, "sell": 3780.0}, "noncash": {"buy": 3715.0, "sell": 3785.0}},
        "cny": {"cash": {"buy": 470.0, "sell": 485.0}, "noncash": {"buy": 468.0, "sell": 487.0}},
    }


@pytest.fixture
def sample_khanbank_response():
    """Sample KhanBank API response."""
    return [
        {"currency": "USD", "cashBuyRate": 3420.5, "cashSellRate": 3450.0, "buyRate": 3415.0, "sellRate": 3455.0},
        {"currency": "EUR", "cashBuyRate": 3720.0, "cashSellRate": 3780.0, "buyRate": 3715.0, "sellRate": 3785.0},
    ]


@pytest.fixture
def sample_golomt_response():
    """Sample Golomt API response - result is dict with currency codes as keys."""
    return {
        "result": {
            "USD": {
                "cash_buy": {"cvalue": 3420.5},
                "cash_sell": {"cvalue": 3450.0},
                "non_cash_buy": {"cvalue": 3415.0},
                "non_cash_sell": {"cvalue": 3455.0},
            },
            "EUR": {
                "cash_buy": {"cvalue": 3720.0},
                "cash_sell": {"cvalue": 3780.0},
                "non_cash_buy": {"cvalue": 3715.0},
                "non_cash_sell": {"cvalue": 3785.0},
            },
        }
    }


@pytest.fixture
def sample_mongolbank_response():
    """Sample MongolBank API response."""
    return {"data": [{"code": "USD", "rate": 3435.0}, {"code": "EUR", "rate": 3750.0}, {"code": "CNY", "rate": 475.0}]}
