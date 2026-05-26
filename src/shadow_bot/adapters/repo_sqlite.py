from typing import List
from sqlalchemy import Engine, Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base, Session
from src.shadow_bot.core.models import Trade, Order
from src.shadow_bot.core.ports import RepoPort

Base = declarative_base()

class BankrollEntity(Base):
    __tablename__ = 'bankroll'
    id = Column(Integer, primary_key=True)
    balance = Column(Float, nullable=False, default=0.0)

class TradeEntity(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String, nullable=False)
    action = Column(String, nullable=False)
    side = Column(String, nullable=False)
    count = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    filled_count = Column(Integer, nullable=False)
    filled_price = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    realized_pnl = Column(Float, nullable=False, default=0.0)

class SQLiteRepo(RepoPort):
    def __init__(self, engine: Engine):
        self.engine = engine
        
    def setup(self):
        Base.metadata.create_all(self.engine)
        # Initialize bankroll if not exists
        with Session(self.engine) as session:
            if not session.query(BankrollEntity).first():
                session.add(BankrollEntity(id=1, balance=0.0))
                session.commit()

    def get_bankroll(self) -> float:
        with Session(self.engine) as session:
            bankroll = session.query(BankrollEntity).filter_by(id=1).first()
            return bankroll.balance if bankroll else 0.0

    def add_bankroll(self, amount: float) -> None:
        with Session(self.engine) as session:
            bankroll = session.query(BankrollEntity).filter_by(id=1).first()
            if bankroll:
                bankroll.balance += amount
                session.commit()

    def deduct_bankroll(self, amount: float) -> None:
        with Session(self.engine) as session:
            bankroll = session.query(BankrollEntity).filter_by(id=1).first()
            if bankroll:
                bankroll.balance -= amount
                session.commit()

    def save_trade(self, trade: Trade) -> None:
        with Session(self.engine) as session:
            entity = TradeEntity(
                ticker=trade.order.ticker,
                action=trade.order.action,
                side=trade.order.side,
                count=trade.order.count,
                price=trade.order.price,
                filled_count=trade.filled_count,
                filled_price=trade.filled_price,
                total_cost=trade.total_cost,
                status=trade.status,
                realized_pnl=trade.realized_pnl
            )
            session.add(entity)
            session.commit()
            trade.id = entity.id

    def update_trade(self, trade: Trade) -> None:
        with Session(self.engine) as session:
            entity = session.query(TradeEntity).filter_by(id=trade.id).first()
            if entity:
                entity.status = trade.status
                entity.realized_pnl = trade.realized_pnl
                session.commit()

    def get_unresolved_trades(self) -> List[Trade]:
        with Session(self.engine) as session:
            entities = session.query(TradeEntity).filter(TradeEntity.status != "resolved").all()
            trades = []
            for e in entities:
                order = Order(ticker=e.ticker, action=e.action, side=e.side, count=e.count, price=e.price)
                trade = Trade(id=e.id, order=order, filled_count=e.filled_count, filled_price=e.filled_price, total_cost=e.total_cost, status=e.status, realized_pnl=e.realized_pnl)
                trades.append(trade)
            return trades

    def get_all_trades(self) -> List[Trade]:
        with Session(self.engine) as session:
            entities = session.query(TradeEntity).all()
            trades = []
            for e in entities:
                order = Order(ticker=e.ticker, action=e.action, side=e.side, count=e.count, price=e.price)
                trade = Trade(id=e.id, order=order, filled_count=e.filled_count, filled_price=e.filled_price, total_cost=e.total_cost, status=e.status, realized_pnl=e.realized_pnl)
                trades.append(trade)
            return trades
