from sqlalchemy import Column, Integer, String, Float, Date, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MandiPriceHistory(Base):
    __tablename__ = "mandi_price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(String, index=True)
    district = Column(String)
    market = Column(String, index=True)
    commodity = Column(String, index=True)
    variety = Column(String)
    grade = Column(String)
    min_price = Column(Float)
    max_price = Column(Float)
    modal_price = Column(Float)
    price_date = Column(Date, index=True)

    __table_args__ = (
        Index("ix_state_commodity_market_date", "state", "commodity", "market", "price_date"),
    )

    def __repr__(self):
        return f"<MandiPriceHistory(id={self.id}, commodity={self.commodity}, market={self.market}, price_date={self.price_date})>"
