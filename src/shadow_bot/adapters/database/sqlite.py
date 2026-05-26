from sqlalchemy import create_engine, Engine, select, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

from shadow_bot.core.ports import RepoPort
from shadow_bot.core.models import Trade
from shadow_bot.adapters.database.models import Base, TradeORM, BankrollStateORM

class SQLiteRepo(RepoPort):
    def __init__(self, db_path: str = "sqlite:///shadow_bot.db") -> None:
        self.engine: Engine = create_engine(
            db_path,
            connect_args={"timeout": 15},
            poolclass=NullPool
        )
        
        # Configure SQLite pragmas for performance and concurrency
        with self.engine.begin() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL;"))
            conn.execute(text("PRAGMA synchronous=NORMAL;"))
            conn.execute(text("PRAGMA foreign_keys=ON;"))
            conn.execute(text("PRAGMA busy_timeout=5000;"))
            
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def save_trade(self, trade: Trade) -> None:
        """Saves an executed trade."""
        with self.SessionLocal() as session:
            trade_orm = TradeORM(
                market_id=trade.market_id,
                order_id=trade.order_id,
                side=trade.side,
                price=trade.price,
                count=trade.count,
                timestamp=trade.timestamp,
            )
            session.add(trade_orm)
            session.commit()

    def get_bankroll(self) -> float:
        """Gets current available bankroll."""
        with self.SessionLocal() as session:
            stmt = select(BankrollStateORM).order_by(BankrollStateORM.id.desc()).limit(1)
            state = session.execute(stmt).scalar_one_or_none()
            if state is None:
                return 0.0
            return float(state.amount)

    def set_bankroll(self, amount: float) -> None:
        """Sets the current available bankroll."""
        with self.SessionLocal() as session:
            new_state = BankrollStateORM(amount=amount)
            session.add(new_state)
            session.commit()
