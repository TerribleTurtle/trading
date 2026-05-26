from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TradeORM(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    market_id: Mapped[str] = mapped_column(String, index=True)
    order_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    side: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    count: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class BankrollStateORM(Base):
    __tablename__ = "bankroll_state"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
